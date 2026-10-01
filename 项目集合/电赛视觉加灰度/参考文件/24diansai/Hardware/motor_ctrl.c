#include "motor_ctrl.h"

uint8_t MOTOR1_ENABLE_FLAG = 0;//电机使能标志位
uint8_t MOTOR2_ENABLE_FLAG = 0;
uint32_t set_motor_speed=3000;




//PWM限幅函数 *a传入要限幅的参数  ABS_MAX限幅大小
void PWM_Limit(int *a, int ABS_MAX){
  if (*a > ABS_MAX)
    *a = ABS_MAX;
  if (*a < -ABS_MAX)
    *a = -ABS_MAX;
}
// 设置电机1的PWM
void Set_Motor1_PWM(int Target_PWM){
	PWM_Limit(&Target_PWM,9999);
	DL_TimerA_setCaptureCompareValue(PWM_0_INST,Target_PWM,GPIO_PWM_0_C1_IDX);
}
// 设置电机2的PWM
void Set_Motor2_PWM(int Target_PWM){
	PWM_Limit(&Target_PWM,9999);
	DL_TimerA_setCaptureCompareValue(PWM_0_INST,Target_PWM,GPIO_PWM_0_C0_IDX);
}
//设置电机1的速度
void Set_Motor1_Speed(int Target_Speed){
	if(MOTOR1_ENABLE_FLAG==1)
	{if(Target_Speed >= 0)//正转
	{Set_Motor1_PWM(Target_Speed);Motor1_Backward();}
	else if(Target_Speed < 0)//反转
	{Set_Motor1_PWM(-Target_Speed);Motor1_Forward();}}
	else {Motor1_Stop();}//输出清零
}
//设置电机2的速度
void Set_Motor2_Speed(int Target_Speed){
	if(MOTOR2_ENABLE_FLAG==1)
	{if(Target_Speed >= 0)//正转
	{Set_Motor2_PWM(Target_Speed);Motor2_Forward();}
	else if(Target_Speed < 0)//反转
	{Set_Motor2_PWM(-Target_Speed);Motor2_Backward();}}
	else {Motor2_Stop();}//输出清零
}
//设置所有电机速度
void SET_MOTORS_SPEED(int Target_Motor2_Speed,int Target_Motor1_Speed){
	Set_Motor1_Speed(Target_Motor1_Speed);Set_Motor2_Speed(Target_Motor2_Speed);
}