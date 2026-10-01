#include "key.h"


uint8_t key1_status = 1;       //开关状态变量
uint8_t key2_status = 1;       //开关状态变量
uint8_t key3_status = 1;       //开关状态变量
uint8_t key4_status = 1;       //开关状态变量

uint8_t car_go_flag=0;


uint8_t KEY_Scan(void)
{
  unsigned char keydata=0;
    static uint8_t key = 0;
     key1_status=KEY1;
     key2_status=KEY2;
     key3_status=KEY3;
     key4_status=KEY4;

     
     if ((key)&&(key1_status == 1) &&( key2_status == 1)&& (key3_status == 1 )&&( key4_status == 1) )    // 无按键按下&&( key2_status == 1)&& (key3_status == 1 )&&( key4_status == 1)
       key--;
    else if ((key1_status == 0 )|| (key2_status == 0) || (key3_status == 0) || (key4_status == 0)) // 任意一个按键按下|| (key2_status == 0) )|| (key3_status == 0) || (key4_status == 0)
    {
     
        if (key1_status == 0)
            keydata=1;
        else if (key2_status == 0)
            keydata=2;
        else if (key3_status == 0)
            keydata=3;
        else if (key4_status == 0)
            keydata=4;
         if(key==0)
      {
        key=5;
       return keydata;
      }
    }
    
    return 0;
}




