#ifndef CODE_KEY_H_
#define CODE_KEY_H_
#include "main.h"
//定义按键引脚  
#define KEY1 			((DL_GPIO_readPins(KEY_PORT,KEY_KEY4_PIN))?1:0)
#define KEY2 			((DL_GPIO_readPins(KEY_PORT,KEY_KEY2_PIN))?1:0)
#define KEY3 			((DL_GPIO_readPins(KEY_PORT,KEY_KEY1_PIN))?1:0)
#define KEY4 			((DL_GPIO_readPins(KEY_PORT,KEY_KEY3_PIN))?1:0)

extern uint8_t key1_status ;       //开关状态变量
extern uint8_t key2_status ;       //开关状态变量
extern uint8_t key3_status ;       //开关状态变量
extern uint8_t key4_status ;       //开关状态变量

uint8_t KEY_Scan(void);


#endif


