#ifndef __GW_GRAY_H__
#define __GW_GRAY_H__

#include "main.h"


extern uint8_t error_flag;//未寻道即标志位
extern uint16_t count_error;//无黑线计时。

extern float error_huidu;
extern int32_t huidu_pid_out;
extern uint8_t turn_left_flag;
extern uint8_t turn_right_flag;
extern uint8_t gray_flag;
extern uint8_t deer_flag;
float Track_err(void);
extern uint8_t TRACK1;
extern uint8_t TRACK2;
extern uint8_t TRACK3;
extern uint8_t TRACK4;
extern uint8_t TRACK5;

uint8_t Get_Infrared_State(void);

#define Read_Huidu_IO1	 ((DL_GPIO_readPins(Huidu_IN1_PORT, Huidu_IN1_PIN)==Huidu_IN1_PIN)?1:0)
#define Read_Huidu_IO2	 ((DL_GPIO_readPins(Huidu_IN2_PORT, Huidu_IN2_PIN)==Huidu_IN2_PIN)?1:0)
#define Read_Huidu_IO3	 ((DL_GPIO_readPins(Huidu_IN3_PORT, Huidu_IN3_PIN)==Huidu_IN3_PIN)?1:0)

#define Read_Huidu_IO4	 ((DL_GPIO_readPins(Huidu_IN4_PORT, Huidu_IN4_PIN)==Huidu_IN4_PIN)?1:0)

#define Read_Huidu_IO5	 ((DL_GPIO_readPins(Huidu_IN5_PORT, Huidu_IN5_PIN)==Huidu_IN5_PIN)?1:0)






#endif 
