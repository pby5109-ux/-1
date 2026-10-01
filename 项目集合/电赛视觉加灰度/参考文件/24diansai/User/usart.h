#ifndef __USART_H__
#define __USART_H__

#include "main.h"
//串口发送单个字符
#define USART0_REC_LEN		200  	//定义最大接收字节数 200

extern uint8_t  USART0_RX_BUF[USART0_REC_LEN]; //接收缓冲,最大USART_REC_LEN个字节.末字节为换行符 
extern uint16_t USART0_RX_STA;         		//接收状态标记


void uart0_send_char(char ch);
//串口发送字符串
void uart0_send_string(char* str);
void usart0_send_byte(unsigned char byte);
void usart0_send_bytes(unsigned char *buf, int len);



void JustFloat_SendArray(uint8_t *string,uint8_t length);
/*将浮点数f转化为4个字节数据存放在byte[4]中*/
void Float_to_Byte(float f,unsigned char byte[]);
//justfloat 数据协议测试
void JustFloat_Test(void);	
//向vofa发送数据  三个数据  三个通道  可视化显示  帧尾
void vofa_sendData(float a,float b,float c);


uint8_t HAL_UART_Transmit( uint8_t *pData, uint16_t Size, uint32_t Timeout);












#endif
