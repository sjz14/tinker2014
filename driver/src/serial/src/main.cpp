#include <string>
#include <ros/ros.h>
#include <ros/package.h>
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <SerialPort.h>
#include <SerialStream.h>
#include "std_msgs/String.h"
#include <QSettings>
#include <QList>
#include "std_msgs/UInt8MultiArray.h"
#include "std_msgs/MultiArrayLayout.h"
#include "std_msgs/MultiArrayDimension.h"

using std::cout;
using std::endl;
using std::string;
using namespace LibSerial;
using namespace std;
SerialStream my_serial_stream ;
char cmd[20];
void orderCallback(const std_msgs::String::ConstPtr& msg)
{
    ROS_INFO("I heard: [%s]",msg->data.c_str());
    if (my_serial_stream) my_serial_stream<<msg->data.c_str();
    strcpy(cmd,msg->data.c_str());
}

int main(int argc, char** argv)
{
    /* Init */
    cout<<"serial"<<endl;
    ros::init(argc, argv, "serialport_driver");
    ros::NodeHandle n;
    ros::Rate rate(40);
    std::string package_path = ros::package::getPath("serial") + "/";
    QSettings settings((package_path + "furoc.ini").c_str(),QSettings::IniFormat);
    int pos = settings.value("pos", 1).toInt();
    printf("pos=%d\n", pos);
    QString dev = settings.value("dev",1).toString();
    printf("preconfig dev = %s\n",dev.toStdString().c_str());
    QString password = settings.value("sudopass",1).toString();
    QString chipset = settings.value("chipset",1).toString();
    printf("selected chipset is %s\n",chipset.toStdString().c_str());
    char command[1024] = "dmesg | grep ";
    strcat(command, chipset.toStdString().c_str());
    char buffer[100] = {0};
    FILE* fp = popen(command, "r");
    char devnum[10] = "NULL";
    while (fgets(buffer,sizeof(buffer),fp)!=NULL)
    {
	int pos;
	char * substr = strstr(buffer,"ttyUSB");
    	if (substr!=0) strncpy(devnum,substr,7);
    }
    pclose(fp);
    printf("%s\n",devnum);
    char sudocommand[100] = "echo ";
    std::stringstream ss;

    if (strcmp(devnum,"NULL") != 0)
    {
	strcat(sudocommand, password.toStdString().c_str());
	strcat(sudocommand, " | sudo -S chmod 777 /dev/");
	strcat(sudocommand, devnum);
	system(sudocommand);
	char devnum2[20] = "/dev/";
	strcat(devnum2,devnum);
	my_serial_stream.Open( devnum2 ) ;
    	ss<<devnum2;
    }
    else
	{
	strcat(sudocommand, password.toStdString().c_str());
	strcat(sudocommand, " | sudo -S chmod 777 /dev/");
	strcat(sudocommand, dev.toStdString().c_str());
	system(sudocommand);
	my_serial_stream.Open( dev.toStdString().c_str() ) ;
    	ss<<dev.toStdString().c_str();

	}
   if (!my_serial_stream){
        std::cout<<"cannot open serial"<<std::endl;
        return -1;
    }

   my_serial_stream.SetBaudRate( SerialStreamBuf::BAUD_57600) ;
   std_msgs::String msg2;
    ros::Rate loop_rate(200);
    ros::Subscriber sub = n.subscribe("order",1000,orderCallback);
    ros::Publisher pub = n.advertise<std_msgs::UInt8MultiArray>("opticflow",100);

   std_msgs::UInt8MultiArray m;

    while(ros::ok())
    {
	my_serial_stream<<"stg000g000g000g000e";
	my_serial_stream<<cmd;
	vector<unsigned char> buffer_opt;
	while (my_serial_stream.rdbuf()->in_avail()>0)
	{
	    	char next_byte;
	    	my_serial_stream.get(next_byte);
		if (next_byte == 0x72)
		   {
 		    my_serial_stream.get(next_byte);
		    if (next_byte == 0x6f)
			{
			    char buff[8];
			    m.data.clear();
			    for (int i =0 ;i< 8 ; i++)
				{
				    my_serial_stream.get(buff[i]);
				    m.data.push_back(buff[i]);
				    cout<<(int)buff[i]<<' ';
				}
				cout<<endl;
			    pub.publish(m);
			}
		   }
	}
	rate.sleep();
	ros::spinOnce();
    }

    my_serial_stream.Close();
    cout<<"bye"<<endl;
    return 0;
}
