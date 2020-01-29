#include <regex>
#include <type_traits>
#include <fstream>
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/imgcodecs.hpp"
#include <stdio.h>
#include <cstdio>
#include <stdlib.h>
#include <algorithm>
#include <string.h>
#include <chrono>
#include <ctime>
#include <sys/time.h>
#include <opencv2/opencv.hpp>
                       

using namespace std;
using namespace cv;
using namespace std::chrono;


//Declaring functions for later use
std::chrono::system_clock::time_point makeTimePoint (int year, int mon, int day, int hour, int min, int sec=0);
std::string asString (const std::chrono::system_clock::time_point& tp);
ofstream featuresfile;

//Defining variables including start time and frametime as well as a Rec obj
Rect Rec(2, 0, 640, 480);
std::chrono::system_clock::time_point firsttime;
std::chrono::system_clock::time_point frametime;
int elapsed_time;

int main(int argc, char *argv[])
{
    high_resolution_clock::time_point t1 = high_resolution_clock::now();

//error handling from input
    if(!(argc==2)) {
      cout << "Usage: " << argv[0] << " <ppm_file> " << endl;
      cout << "         ysu_record: " << endl ;
      cout << "            - captures thermal imager and creates PPM.gz files with timestamped names." << endl ;
      cout << "         ysu_readPPM   " << endl;
      cout << "            - reads any PPM.gz file and creates an image and a csv file for analysis. " << endl ;
      cout << "         ysu_readZLST   " << endl ;
      cout << "            - reads a text list file that includes an ordered list of PPM.gz files. " << endl ;
      cout << "              The program displays and records a video and creates a feature file " << endl ;
      cout << "              with probe temperatures.  Each line of the feature file has the probed " << endl ;
      cout << "              temperatures from one PPM file. " << endl ;
      cout << "         ysu_efficient    " << endl ;
      cout << "            - reads a text list file that includes an ordered list of PPM.gz files.   " << endl ;
      cout << "              The program displays and records a video for a region of interest and   " << endl ;
      cout << "              creates a feature file with probe temperatures captured.  Each line   " << endl ;
      cout << "              of the feature file has the probed temperature from one PPM file.  " << endl ;
      cout << "              Two composite images are created - max temp and the integration of " << endl ;
      cout << "              termperature difference with the pixel_threshold value." << endl ;
      cout << "         ysu_meltpool  " << endl; 
      cout << "            - reads a text list file that includes an ordered list of PPM.gz files." << endl; 
      cout << "              The program displays an image of a window centered around the melt pool" << endl; 
      cout << "              and also creates a CSV file for analysis. " << endl;
      cout << "              The code depends a stable high temperature point to which to register." << endl;
      cout << "         ysu_point  " << endl;
      cout << "            - reads a text list file that includes an ordered list of PPM.gz files. " << endl;
      cout << "              The program displays an image of a window centered around a specified " << endl;
      cout << "              location and also creates a CSV file for analysis. " << endl;
      cout << "         python heat.py - reads a single csv file and creates a heat map." << endl;
      cout << "            - reads any PPM.gz file and creates an image and a csv file for analysis. " << endl ;
      return -1;
      }
     
    //Size of desired output
      int              outw = 640;
      int              outh = 480;

      std::string      timetext;
      unsigned short   value;
      unsigned short   value_fake;
      unsigned short   old_value = 0;
      unsigned char    lsb;
      unsigned char    msb;
      int              base_seconds;
      int              long_frame_count = 0;
      int              frame_start;
      int              frame_end;
      int              frame_size = outw * outh;
   
      std::streampos   fileSize;
      int              fileindex = 1;
      char           * file_buffer;
      unsigned short * frame_buffer;
      frame_buffer = new unsigned short [frame_size];
      string ppmfile_string; 
      string zppmfile_string;
      string colorizedPath;

    //PPM path shoul be first arg
      ppmfile_string = argv[1];
      colorizedPath = ppmfile_string + "Colorized.jpg";


      regex r2("(\\S+)\\.gz"); 
      smatch m2;
      if(regex_match(ppmfile_string,m2,r2)) 
          {
          ppmfile_string = m2[1];
          //cout << "1 " << ppmfile_string << endl;
          } 
      zppmfile_string = "gunzip " + ppmfile_string + ".gz"; 
      //cout << "2 " << zppmfile_string << endl;
      std::system(zppmfile_string.c_str());
 
    //Opening PPM file
       int index = 0;
       std::ifstream  ppmfile(ppmfile_string, ios::in|ios::binary|ios::ate);
       if (!ppmfile.is_open()) 
             {
             cerr << "Could not open ppm file " << index << endl;
             return -1;
             }
       else 
             {
             cerr << "Opened ppm file" << argv[1] << endl;
             }

     //creating a textfile to write to 
      std::string      inputstring = argv[1];
      featuresfile.open(inputstring + ".txt");
      if (!featuresfile.is_open()) 
            {
            cerr << "Could not open text feature file for write\n";
            return -1;
            }

    //Making sure correct file is loaded being opened as well as creating a timestamp
      regex r1("(\\S+)\\.PPM"); 
      smatch m1;
      string timestamp;
      string inputfile     = argv[1];
      if(regex_match(inputfile, m1, r1)) 
          {
          timestamp = m1[1];
          } 

      ppmfile.seekg(0, std::ios::end);
      fileSize = ppmfile.tellg();
      ppmfile.seekg(0, std::ios::beg);

      cout << "Timestamp " << timestamp << endl;
      cout << "file size = " << fileSize << endl ;

    //reading the PPM
      file_buffer = new char [fileSize];
      ppmfile.read (file_buffer, fileSize);
      frame_start = 18; 
      frame_end = ((2*frame_size) + 18); 
    //Establishing variables to deal with data
      int z = 0;
      int minval = 900;
      int maxval = 0;
    
    //Dealing with data and placing in frame_buffer
      for(int k = frame_start; k < frame_end; k = k + 2)
              {
              lsb = (unsigned char)(file_buffer[k]);
              msb = (unsigned char)(file_buffer[k+1]);
              value = (unsigned short)msb*256 + (unsigned short)lsb;
              frame_buffer[z] = value;
              z++;
              }

          cv::Mat cv_img(cv::Size(outw, outh), CV_16UC1, &frame_buffer[0], cv::Mat::AUTO_STEP);
          cv::Size scv_img = cv_img.size();


          double high,low;
          cv::Point wherehigh, wherelow;
          cv::minMaxLoc(cv_img,&high,&low,&wherehigh,&wherelow);
          cv::Mat cv_img2;
          cv::Mat cv_img3;
          cv::Mat color;
          cv_img.convertTo(cv_img2, CV_8UC1);
          //cv::equalizeHist(cv_img2, cv_img2);
          applyColorMap(cv_img2, color, cv::COLORMAP_JET);
          //cv::Rect roi( roiVertexXCoordinate, roiVertexYCoordinate, roiWidth, roiHeight );
          //cv::Mat image_roi = inputImage( roi );
          cv::Scalar avgPixelIntensity = cv::mean( cv_img );
          float average_pixel = avgPixelIntensity.val[0];
          timetext = "Frame " + std::to_string(index) + " " + timestamp + " average = " + std::to_string(average_pixel) + " C";
          std::cout << timetext << std::endl;   
          //putText(color, timetext, Point(50, 50), FONT_HERSHEY_SIMPLEX, 0.5, Scalar(255, 255, 255), 1);
          cout << cv_img2.at<short>(20,20) << endl ;
          cv::imshow("image", color);
          cv::imwrite(colorizedPath, color);
          cv::waitKey(0);

          for(int i=0;i<640;i++){
             for(int j=0;j<480;j++){
               featuresfile << cv_img.at<short>(j,i) << ", ";
              } 
             featuresfile << std::endl;
          }

          ppmfile.close();
          //ppmfile_string = "gzip " + ppmfile_string;
          std::system(ppmfile_string.c_str());
          delete[] file_buffer;

          index = index + 1;

     delete[] frame_buffer;
     return 0;
}


std::string asString (const std::chrono::system_clock::time_point& tp)
{
   // convert to system time:
   std::time_t t = std::chrono::system_clock::to_time_t(tp);
   std::string ts = ctime(&t);   // convert to calendar time
   ts.resize(ts.size()-1);       // skip trailing newline
   return ts;
}

std::chrono::system_clock::time_point makeTimePoint (int year, int mon, int day, int hour, int min, int sec)
{
   struct std::tm t;
   t.tm_sec = sec;        // second of minute (0 .. 59 and 60 for leap seconds)
   t.tm_min = min;        // minute of hour (0 .. 59)
   t.tm_hour = hour;      // hour of day (0 .. 23)
   t.tm_mday = day;       // day of month (0 .. 31)
   t.tm_mon = mon-1;      // month of year (0 .. 11)
   t.tm_year = year-1900; // year since 1900
   t.tm_isdst = -1;       // determine whether daylight saving time
   std::time_t tt = std::mktime(&t);
   if (tt == -1) {
       throw "no valid system time";
   }
   return std::chrono::system_clock::from_time_t(tt);
}
