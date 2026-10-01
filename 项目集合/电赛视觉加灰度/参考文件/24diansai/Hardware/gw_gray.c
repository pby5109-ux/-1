
#include "gw_gray.h"
#include "delay.h"


uint8_t error_flag=0;//未寻道即标志位
uint16_t count_error=0;//无黑线计时。
uint16_t angel_target=0;//未寻道即标志位


uint8_t turn_left_flag=0;
uint8_t turn_right_flag=0;
uint8_t gray_flag=0;

int32_t huidu_pid_out=0;

float error_huidu=0;
 uint8_t TRACK1=0;
 uint8_t TRACK2=0;
 uint8_t TRACK3=0;
 uint8_t TRACK4=0;
 uint8_t TRACK5=0;


u8 Get_Infrared_State(void)
{
		//1扫到黑线，0没扫到
	u8 state = 0;
	TRACK1= Read_Huidu_IO1<<4 ;
	TRACK2= Read_Huidu_IO2<<3 ;
	TRACK3= Read_Huidu_IO3<<2 ;
	TRACK4= Read_Huidu_IO4<<1 ;
	TRACK5= Read_Huidu_IO5<<0 ;
	state=(u8)(TRACK1|TRACK2|TRACK3|TRACK4|TRACK5);//拼接成五位数据，最高位为为传感器的的左1，最低为为传感器的右1
	return state;
}

float Track_err(void)
{
	u8 state =  Get_Infrared_State();
	float error;
	//车在线的右边err为正值，左边为负数
	switch(state)
	{  

		case 4:   //00100  
		error= 0 ;	  break;
		case 12:   //01100 
		error= 2.3 ;	  break;
		case 6:   //00110 
		error= -2.3 ;	  break;
		case 0:   //00000  
		error= 0;	  break;
		case 24: // 11000
			turn_left_flag=1;
		break;
		case 28: // 11100
			turn_left_flag=1;
		break;
		case 7: // 00111
			turn_right_flag=1;
		break;
		case 3: // 00011
			turn_right_flag=1;
		break;
		case 8:   //01000    
		error= 7;//3 ;	 
		break;	
		case 16:   //10000    
		error= 20;//3 ;
		
		break;
		case 2:   //00010    
		error= -7;//3 ;	 
		break;	
		case 1:   //00001    
		error= -20;//3 ;
		
		break;
		
		
		default: 
		error=0;   break;
	}
	
	if(error==0)
	{
	 error_flag=1;
	} 
	else
	{
	error_flag=0;
	}
	
	return error;
}



