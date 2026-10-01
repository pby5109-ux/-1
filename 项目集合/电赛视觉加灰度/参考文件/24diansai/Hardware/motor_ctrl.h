#ifndef __MOTOR_CTRL_H__
#define __MOTOR_CTRL_H__

#include "main.h"


/*-------------------------------------------------------------------------------------------*/
/*------------------------------------电机操作函数-------------------------------------------*/
/*-------------------------------------------------------------------------------------------*/
#define MOTORS_ENABLE()			{MOTOR1_ENABLE_FLAG = 1;MOTOR2_ENABLE_FLAG = 1;}
#define MOTORS_DISABLE()		{MOTOR1_ENABLE_FLAG = 0;MOTOR2_ENABLE_FLAG = 0;}

#define AIN1(x)   x?DL_GPIO_setPins(Motor_Ctrl_AIN1_PORT, Motor_Ctrl_AIN1_PIN):DL_GPIO_clearPins(Motor_Ctrl_AIN1_PORT, Motor_Ctrl_AIN1_PIN)
#define AIN2(x)   x?DL_GPIO_setPins(Motor_Ctrl_AIN2_PORT, Motor_Ctrl_AIN2_PIN):DL_GPIO_clearPins(Motor_Ctrl_AIN2_PORT, Motor_Ctrl_AIN2_PIN)
#define BIN1(x)   x?DL_GPIO_setPins(Motor_Ctrl_BIN1_PORT, Motor_Ctrl_BIN1_PIN):DL_GPIO_clearPins(Motor_Ctrl_BIN1_PORT, Motor_Ctrl_BIN1_PIN)
#define BIN2(x)   x?DL_GPIO_setPins(Motor_Ctrl_BIN2_PORT, Motor_Ctrl_BIN2_PIN):DL_GPIO_clearPins(Motor_Ctrl_BIN2_PORT, Motor_Ctrl_BIN2_PIN)

#define Motor1_Forward()	{AIN1(1);AIN2(0);}
#define Motor1_Backward()	{AIN1(0);AIN2(1);}
#define Motor1_Stop()		  {AIN1(0);AIN2(0);}

#define Motor2_Forward()	{BIN1(1);BIN2(0);}
#define Motor2_Backward()	{BIN1(0);BIN2(1);}
#define Motor2_Stop()		{BIN1(0);BIN2(0);}

void Set_Motor1_Speed(int Target_Speed);
void Set_Motor2_Speed(int Target_Speed);
void SET_MOTORS_SPEED(int Target_Motor2_Speed,int Target_Motor1_Speed);


void Set_Motor2_PWM(int Target_PWM);
void Set_Motor1_PWM(int Target_PWM);
extern uint8_t MOTOR1_ENABLE_FLAG;
extern uint8_t MOTOR2_ENABLE_FLAG;
extern uint32_t set_motor_speed;





#endif
