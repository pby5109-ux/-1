#include "main.h"
#define ti2_x 1200
#define ti2_y 1600


uint8_t flag_ti=0;
uint8_t flag_step=0;
uint8_t start_flag=0;
uint32_t servo_x=1200;
uint32_t servo_y=1600;
uint32_t left_pwm=0;
uint32_t right_pwm=0;
uint8_t N=1;//定义N圈
uint32_t x_mid=400;
uint32_t y_mid=260;

uint32_t x_loc=0;
uint32_t y_loc=0;

float yaw_now=0;
void uart_loc();


uint8_t UI_shift=0;
void datafun();
void keyloc()
{
 unsigned char keynum=0;
	keynum=KEY_Scan();
	if(keynum!=0)
	{
	 switch(keynum)
	 {
		 case 1:
			 UI_shift=(UI_shift+1)%6;
			
		 
		 
		 OLED_Clear();
		 break;
		 case 2:
			flag_ti=(flag_ti+1)%6;
	
		 
		 OLED_Clear();
		 break;
		 case 3:
			
			if(flag_ti==1)
		 {
		  N++;
		 }
		 OLED_Clear();
		 break;
		 case 4:
			 
				if(UI_shift==1)
				{
				start_flag^=1;
				flag_step=0;
					memset(USART0_RX_BUF,0,sizeof(USART0_RX_BUF)); 
				USART0_RX_STA=0;
				}
				else if(flag_ti==1)
				 {
					N--;
				 } 
		 OLED_Clear();
		 break;
		 
	 }
	}
}
uint8_t Car_Mode = Angle_Mode;//调试模式
float Basic_Speed = 30;									//电机目标速度
uint8_t OLED_View_Select = 1;							//OLED选择界面变量
/*-------------------------------------------------------------------------------------------*/
/*---------------------------------------主函数----------------------------------------------*/
/*-------------------------------------------------------------------------------------------*/
int main(void)
{
	SYSCFG_DL_init();//芯片资源初始化,由SysConfig配置软件自动生成
	//硬件初始化
  OLED_Init();//初始化OLED
	mpu6050_init();//初始化MPU6050
	Pid_Init();
	NVIC_EnableIRQ_Init();//NVIC中断配置初始化
	MOTORS_ENABLE();
	BEEP(1);
	set_pwm(servo_x,servo_y);
	SET_MOTORS_SPEED(0,0);
	while(1)
	{keyloc();
			
		
		
		
		OLED_Show_Proc();//OLED显示函数		
	}
}
void uart_loc()
{
 uint8_t i=0;

	
	static uint16_t last_Y=0;
	static uint16_t last_X=0;
	static uint16_t X_pwm=0;
	static uint16_t Y_pwm=0;
	if((USART0_RX_STA & 0x8000))    // 是否接收到数据
{

			sscanf((char *)USART0_RX_BUF,"(%d,%d)",&x_loc,&y_loc);
	
				x_loc = LPF_1st(last_X,x_loc,0.386f);
				y_loc = LPF_1st(last_Y,y_loc,0.386f);
				
				if((x_loc>=last_X)&&((x_loc-last_X)<=3)&&((y_loc-last_Y)<=3))
				{
				;
				}
				else if((x_loc<last_X)&&((last_X-x_loc)<=3)&&((last_Y-y_loc)<=3))
				{
				;
				}
				else
				{
				if((x_loc!=0)||(y_loc!=0))
								{
								 X_pwm=Xs_pid(x_loc,x_mid);
							 Y_pwm=Ys_pid(y_loc,y_mid);
								}
								set_pwm(ti2_x-X_pwm,ti2_y+Y_pwm);
				}	
			 

				
				memset(USART0_RX_BUF,0,sizeof(USART0_RX_BUF)); 
				USART0_RX_STA=0;
				last_Y=y_loc;
				last_X=x_loc;
}
}
void datafun()
{
	
	if((start_flag))
	{	
		switch(flag_ti)
		{
			case 1:
				switch(flag_step)
				{
					case 0:
					error_huidu=Track_err();
					huidu_pid_out=position_pid(error_huidu ,0); //第一次循迹
					left_pwm=set_motor_speed-huidu_pid_out;
					right_pwm=set_motor_speed+huidu_pid_out;
					SET_MOTORS_SPEED(left_pwm,right_pwm);
					if(Measure_Distance>=345*N)
					{
					 SET_MOTORS_SPEED(0,0);
						flag_step=2;
					}
					else if(turn_left_flag)
					{
					turn_left_flag=0;
						flag_step++;
						yaw_now=mpu6050.Yaw;
					}
					else if(turn_right_flag)
					{
					turn_right_flag=0;
						flag_step=3;
						yaw_now=mpu6050.Yaw;
					}
					break;
					case 1:
				  
					
					SET_MOTORS_SPEED(1000,4000);
					
					if(mpu6050.Yaw>=yaw_now+70)
					{
						flag_step=0;
					}
					break;
					case 2:
					
					break;
					case 3:
					SET_MOTORS_SPEED(4000,1000);
					
					if(mpu6050.Yaw<=yaw_now-70)
					{
						flag_step=0;
					}
					break;
					
					
				}
			break;
			case 2:
				 uart_loc();
				
					
			break;
			case 3:
				uart_loc();
			
			break;
					case 4:
						uart_loc();
					switch(flag_step)
				{
					case 0:
					error_huidu=Track_err();
					huidu_pid_out=position_pid(error_huidu ,0); //第一次循迹
					left_pwm=set_motor_speed-huidu_pid_out;
					right_pwm=set_motor_speed+huidu_pid_out;
					SET_MOTORS_SPEED(left_pwm,right_pwm);
					if(Measure_Distance>=355)
					{
					 SET_MOTORS_SPEED(0,0);
						flag_step=2;
					}
					else if(turn_left_flag)
					{
					turn_left_flag=0;
						flag_step++;
						yaw_now=mpu6050.Yaw;
					}
					else if(turn_right_flag)
					{
					turn_right_flag=0;
						flag_step=3;
						yaw_now=mpu6050.Yaw;
					}
					break;
					case 1:
				  
					
					SET_MOTORS_SPEED(1000,4000);
					
					if(mpu6050.Yaw>=yaw_now+70)
					{
						flag_step=0;
					}
					break;
					case 2:
					
					break;
					case 3:
					SET_MOTORS_SPEED(4000,1000);
					
					if(mpu6050.Yaw<=yaw_now-70)
					{
						flag_step=0;
					}
					break;
					
					
				}
					break;
					case 5:
						
						uart_loc();
					switch(flag_step)
				{
					case 0:
					error_huidu=Track_err();
					huidu_pid_out=position_pid(error_huidu ,0); //第一次循迹
					left_pwm=set_motor_speed-huidu_pid_out;
					right_pwm=set_motor_speed+huidu_pid_out;
					SET_MOTORS_SPEED(left_pwm,right_pwm);
					if(Measure_Distance>=355*2)
					{
					 SET_MOTORS_SPEED(0,0);
						flag_step=2;
					}
					else if(turn_left_flag)
					{
					turn_left_flag=0;
						flag_step++;
						yaw_now=mpu6050.Yaw;
					}
					else if(turn_right_flag)
					{
					turn_right_flag=0;
						flag_step=3;
						yaw_now=mpu6050.Yaw;
					}
					break;
					case 1:
				  
					
					SET_MOTORS_SPEED(0,6000);
					
					if(mpu6050.Yaw>=yaw_now+70)
					{
						flag_step=0;
					}
					break;
					case 2:
					
					break;
					case 3:
					SET_MOTORS_SPEED(6000,0);
					
					if(mpu6050.Yaw<=yaw_now-70)
					{
						flag_step=0;
					}
					break;
					
					
				}
					break;
		}
	
		
	 
	}
	
	
}
	
uint8_t data_ready=0;
	/*---------------------------------------------------------------------------------------*/
/*------------------------------定时器A1的1ms中断服务函数------------------------------------*/
/*-------------------------------------------------------------------------------------------*/
void TIMER_0_INST_IRQHandler(void)//定时器中断服务函数
{
	static uint16_t count_10ms=0;
	static uint16_t count_100ms=0;
	static uint16_t t=0;
	static uint16_t count_t=0;
	static uint16_t count_t2=0;
		
	switch (DL_TimerA_getPendingInterrupt(TIMER_0_INST)) 
	{
		 case DL_TIMERA_IIDX_LOAD:
		 {
			 
			datafun();
			 
			
			 if(++count_10ms>=10)//定时100ms
			 {AHRS_Geteuler();
				 
				  MEASURE_MOTORS_SPEED();
				 
				 count_10ms=0;
				 
				
			
				 
			 }
			
			  if(++count_100ms>=100)//定时100ms
			 {count_100ms=0;
				 led1_toggle();
				 

				 
			 }
			 
			if(++t>=1000)//定时1s（用于判断程序还在运行）
			{t=0;
				
				led2_toggle();

				
				
				
			}
		}break;
		 default:break;
	 }
}



/*-------------------------------------------------------------------------------------------*/
/*-------------------------------------OLED显示界面------------------------------------------*/
/*-------------------------------------------------------------------------------------------*/
void OLED_Show_Proc(void)
{
	switch(UI_shift)
	{
		case 0://主界面
		{
			OLED_ShowString(46,0,(uint8_t *)"Main",16,1);
			OLED_ShowString(0,16,(uint8_t *)"ti:",16,1);OLED_ShowNum(30,16,flag_ti,1,16,1);OLED_ShowString(40,16,(uint8_t *)"N:",16,1);OLED_ShowNum(60,16,N,1,16,1);
			OLED_ShowString(0,32,(uint8_t *)"step:",16,1);OLED_ShowNum(50,32,flag_step,2,16,1);
			OLED_ShowString(0,48,(uint8_t *)"tl:",16,1);OLED_ShowNum(40,48,turn_left_flag,1,16,1);OLED_ShowString(50,48,(uint8_t *)"tr:",16,1);OLED_ShowNum(80,48,turn_right_flag,1,16,1);
			OLED_Update();
		}break;
		case 1://角度数据读取界面
		{
			OLED_ShowString(40,0,(uint8_t *)"Angle",16,1);
			OLED_ShowString(0,16,(uint8_t *)"Pit:",16,1);OLED_ShowFloatNum(35,16,mpu6050.Pitch,3,2,16,1);
			OLED_ShowString(0,32,(uint8_t *)"Rol:",16,1);OLED_ShowFloatNum(35,32,mpu6050.Roll,3,2,16,1);
			OLED_ShowString(0,48,(uint8_t *)"Yaw:",16,1);OLED_ShowFloatNum(35,48,mpu6050.Yaw,3,2,16,1);
			OLED_Update();
		}break;
		case 2://灰度界面
		{
			OLED_ShowString(0,0, (uint8_t *)"hd",16,1);OLED_ShowNum(26,0, Read_Huidu_IO1,1,16,1);OLED_ShowNum(36,0,Read_Huidu_IO2,1,16,1);\
			OLED_ShowNum(46,0,Read_Huidu_IO3,1,16,1);OLED_ShowNum(56,0,Read_Huidu_IO4,1,16,1);OLED_ShowNum(66,0,Read_Huidu_IO5,1,16,1);
		
			OLED_ShowString(0,16,(uint8_t *)"e_hd:",16,1);OLED_ShowSignedNum(40,16,servo_x,4,16,1);
			OLED_ShowString(0,32,(uint8_t *)"hd_pid:",16,1);OLED_ShowSignedNum(76,32,servo_y,4,16,1);
			
			OLED_Update();
		}break;
		case 3://电机原始数据获取
		{
			
			OLED_ShowString(0,0,(uint8_t *)"LE:",16,1);OLED_ShowSignedNum(26,0,Motor2_Speed,3,16,1);OLED_ShowString(60,0,(uint8_t *)"L:",16,1);OLED_ShowSignedNum(80,0,Motor2_Lucheng,4,16,1);
			OLED_ShowString(0,16,(uint8_t *)"RE:",16,1);OLED_ShowSignedNum(26,16,Motor1_Speed,3,16,1);OLED_ShowString(60,16,(uint8_t *)"R:",16,1);OLED_ShowSignedNum(80,16,Motor1_Lucheng,4,16,1);
			OLED_ShowString(0,32,(uint8_t *)"LP:",16,1);OLED_ShowSignedNum(26,32,left_pwm,4,16,1);
			OLED_ShowString(0,48,(uint8_t *)"RP:",16,1);OLED_ShowSignedNum(26,48,right_pwm,4,16,1);
			OLED_Update();
		}break;
		case 4://串口接收数据
		{
			OLED_ShowString(26,0,(uint8_t *)"recvdata",16,1);
			OLED_ShowString(0,16,(uint8_t *)"X_loc:",16,1);OLED_ShowNum(60,16,x_loc,3,16,1);
			OLED_ShowString(0,32,(uint8_t *)"Y_loc:",16,1);OLED_ShowNum(60,32,y_loc,3,16,1);
			
			OLED_Update();
		}break;
//		case 4://zuo边电机PID显示
//		{
//			OLED_ShowString(26,0,(uint8_t *)"vel_PID_left",16,1);
//			OLED_ShowString(0,16,(uint8_t *)"KP:",16,1);OLED_ShowFloatNum(40,16,MotorL.Kp,1,3,16,1);
//			OLED_ShowString(0,32,(uint8_t *)"KI:",16,1);OLED_ShowFloatNum(40,32,MotorL.Ki,1,3,16,1);
//			OLED_ShowString(0,48,(uint8_t *)"Kd:",16,1);OLED_ShowFloatNum(26,48,MotorL.Kd,1,3,16,1);
//			OLED_Update();
//		}break;
		case 5://右PID显示
		{
			OLED_ShowString(26,0,(uint8_t *)"vel_PID_right",16,1);
			OLED_ShowString(0,16,(uint8_t *)"KP:",16,1);OLED_ShowFloatNum(40,16,MotorR.Kp,1,3,16,1);
			OLED_ShowString(0,32,(uint8_t *)"KI:",16,1);OLED_ShowFloatNum(40,32,MotorR.Ki,1,3,16,1);
			OLED_ShowString(0,48,(uint8_t *)"Kd:",16,1);OLED_ShowFloatNum(26,48,MotorR.Kd,1,3,16,1);
			OLED_Update();
		}break;
		case 6://距离环PID显示
		{   
			//OLED_ShowString(20,0,(uint8_t *)"recvdata",16,1);
//			OLED_ShowHexNum(26,0,char1,3,16,1);
//			OLED_ShowString(0,16,(uint8_t *)"Kp:",16,1);OLED_ShowHexNum(26,16,char2,3,16,1);
//			OLED_ShowString(0,32,(uint8_t *)"Ki:",16,1);OLED_ShowHexNum(26,32,char3,3,16,1);
//			OLED_ShowString(0,48,(uint8_t *)"Kd:",16,1);OLED_ShowHexNum(26,48,char4,3,16,1);
//			OLED_Update();
		}break;
		case 7://角速度环PID显示
		{   
//			OLED_ShowString(30,0,(uint8_t *)"Gyro_PID",16,1);
//			OLED_ShowString(0,16,(uint8_t *)"Kp:",16,1);OLED_ShowFloatNum(26,16,pid_Gyro.Kp,3,3,16,1);
//			OLED_ShowString(0,32,(uint8_t *)"Ki:",16,1);OLED_ShowFloatNum(26,32,pid_Gyro.Ki,3,3,16,1);
//			OLED_ShowString(0,48,(uint8_t *)"Kd:",16,1);OLED_ShowFloatNum(26,48,pid_Gyro.Kd,3,3,16,1);
//			OLED_Update();
		}break;
		case 8://角度环PID显示
		{   
//			OLED_ShowString(28,0,(uint8_t *)"Angle_PID",16,1);
//			OLED_ShowString(0,16,(uint8_t *)"Kp:",16,1);OLED_ShowFloatNum(26,16,pid_Angle.Kp,3,3,16,1);
//			OLED_ShowString(0,32,(uint8_t *)"Ki:",16,1);OLED_ShowFloatNum(26,32,pid_Angle.Ki,3,3,16,1);
//			OLED_ShowString(0,48,(uint8_t *)"Kd:",16,1);OLED_ShowFloatNum(26,48,pid_Angle.Kd,3,3,16,1);
//			OLED_Update();
		}break;
		case 9://角速度环看数据（切换按键显示界面，没有此界面，需要添加界面，需要去key.c中KEY_PROC()中修改
		{   
//			OLED_ShowFloatNum(0,0,pid_Gyro.Kp,3,3,16,1);
//			OLED_ShowFloatNum(0,16,pid_Gyro.Ki,3,3,16,1);
//			OLED_ShowFloatNum(0,32,Target_Gyro,3,3,16,1);
//			OLED_ShowFloatNum(0,48,Gyro_Z_Measeure,3,3,16,1);
//			OLED_Update();
		}break;
		default:break;
	}
}
/*-------------------------------------------------------------------------------------------*/
/*-----------------------------------所有中断初始化------------------------------------------*/
/*-------------------------------------------------------------------------------------------*/
void NVIC_EnableIRQ_Init(void)
{
	//清除串口0中断标志
    NVIC_ClearPendingIRQ(UART_0_INST_INT_IRQN);
    //使能串口0中断
    NVIC_EnableIRQ(UART_0_INST_INT_IRQN);
	//清除定时器中断标志
    NVIC_ClearPendingIRQ(TIMER_0_INST_INT_IRQN);
    //使能定时器中断
    NVIC_EnableIRQ(TIMER_0_INST_INT_IRQN);
	//定时器A开始计数
	DL_TimerA_startCounter(TIMER_0_INST);
	//编码器中断使能
	NVIC_EnableIRQ(Encoder_INT_IRQN);

	
}

