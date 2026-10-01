#ifndef __LINEFOLLOW_H_
#define __LINEFOLLOW_H_

#include "stdint.h"
#include "stdbool.h"
#include <string.h>
#include "main.h"

#define LineFollow_ADDRESS		     0x5D
#define LineFollow_STATE_REG			 0x05
#define LineFollow_ANALOG_REG			 0x06
#define LineFollow_THRESHOLD_REG   0x16

#define LINEFOLLOW_FRAME_HEADER1   0x55
#define LINEFOLLOW_FRAME_HEADER2   0xAA
#define LINEFOLLOW_CMD_NULL   0

#pragma pack(1)
typedef struct {
    uint8_t header_1;
    uint8_t header_2;
    union {
        struct {
            uint8_t command;
            uint8_t length;
            uint8_t args[16];
        } elements;
    };
}LineFollowCmdTypeDef;
#pragma pack()

typedef enum {
    LINEFOLLOW_RECV_STARTBYTE_1,
    LINEFOLLOW_RECV_STARTBYTE_2,
    LINEFOLLOW_RECV_COMMAND,
    LINEFOLLOW_RECV_LENGTH,
    LINEFOLLOW_RECV_ARGUMENTS,
    LINEFOLLOW_RECV_CHECKSUM,
} LineFollowUartRecvState;

typedef enum {
    LINEFOLLOW_WRITE_DATA_READY,
		LINEFOLLOW_WRITE_DATA,
    LINEFOLLOW_WRITE_DATA_FINISH,
    LINEFOLLOW_READ_DATA,
		LINEFOLLOW_READ_DATA_FINISH,	
		LINEFOLLOW_READ_DATA_ERROR
} LineFollowUartITState;

typedef enum {
		LINEFOLLOW_MODE_MANUAL,
		LINEFOLLOW_MODE_AUTOMATIC_STATE,
		LINEFOLLOW_MODE_AUTOMATIC_ANALOG,
		LINEFOLLOW_MODE_AUTOMATIC_THRESHOLD,
} LineFollowUartMode;

typedef enum {
		LINEFOLLOW_MODE_MANUAL_NULL,
		LINEFOLLOW_MODE_MANUAL_STATE,
		LINEFOLLOW_MODE_MANUAL_ANALOG,
		LINEFOLLOW_MODE_MANUAL_THRESHOLD,
} LineFollowManualCmd;

typedef struct LineFollowHandle LineFollowHandleTypeDef;
struct LineFollowHandle
{
	uint16_t dev_addr;
	uint8_t results[16];
	uint16_t data[8];
	
	uint8_t transmit_status;
	uint8_t receive_status;

	uint8_t (*write_data)(LineFollowHandleTypeDef* self, uint8_t* pdata, uint16_t size);
	uint8_t (*read_data)(LineFollowHandleTypeDef* self, uint8_t* pdata, uint16_t size);
	
	
	LineFollowUartITState it_state; 
	LineFollowUartRecvState rx_state;
	LineFollowCmdTypeDef rx_frame;
	uint32_t rx_args_index;

	uint8_t tx_frame;
	uint32_t tx_byte_index;
	bool tx_only;
	uint8_t work_mode;
	uint8_t manual_mode;

	int8_t (*LineFollow_write_and_read)(LineFollowHandleTypeDef *self, uint8_t, bool tx_only);

	
};

extern LineFollowHandleTypeDef LineFollow;


/**
 * @brief LineFollowUART初始化
 * 
 */
void LineFollowUART_init(uint8_t Mode);

/**
 * @brief LineFollowUART_State获取传感器状态数据
 */
bool LineFollowUART_State(LineFollowHandleTypeDef* State);

/**
 * @brief LineFollowUART_Analog获取传感器模拟值数据
 */
bool LineFollowUART_Analog(LineFollowHandleTypeDef* Analog);

/**
 * @brief LineFollowUART_Threshold获取传感器阈值数据
 */
bool LineFollowUART_Threshold(LineFollowHandleTypeDef* Threshold);


/**
 * @brief 校验和计算内联函数
 * 
 * @param  buf      需要计算校验和的数组
 * @return uint8_t  校验和计算结构
 */
static inline uint8_t LineFollow_checksum(const uint8_t buf[])
{
    uint16_t temp = 0;
    for (int i = 2; i < buf[3] + 4; ++i) {
        temp += buf[i];
    }
    return (uint8_t)(~temp);
}

/**
 * @brief   巡线数据接收处理内联函数
 * 
 * @param   self             指向LineFollowHandleTypeDef类型的指针
 * @param   rx_byte          接收到的数据（单个字节）
 * @return  int              当前校验结果
 *    @arg   -1   帧头1校验成功OR失败
 *    @arg   -2   帧头2校验成功OR失败
 *    @arg    1   命令校验完毕
 *    @arg   -3   数据包长度校验失败
 *    @arg    2   数据包长度校验成功
 *    @arg    3   数据接收完成
 *    @arg  -99   校验和匹配失败
 *    @arg    0   校验和匹配成功
 *    @arg -100   未知错误
 */
static inline int LineFollow_rx_handler(LineFollowHandleTypeDef *self, uint8_t rx_byte)
{
	if((self->work_mode == LINEFOLLOW_MODE_MANUAL && self->manual_mode == LINEFOLLOW_MODE_MANUAL_STATE) || \
				self->work_mode == LINEFOLLOW_MODE_AUTOMATIC_STATE)
	{
		self->results[0] = rx_byte;
		self->manual_mode = LINEFOLLOW_MODE_MANUAL_NULL;
	}
	else
	{
		switch (self->rx_state) {
			case LINEFOLLOW_RECV_STARTBYTE_1: {
					self->rx_state = LINEFOLLOW_FRAME_HEADER1 == rx_byte ? LINEFOLLOW_RECV_STARTBYTE_2 : LINEFOLLOW_RECV_STARTBYTE_1;
					if(self->rx_state == LINEFOLLOW_RECV_STARTBYTE_1)
					{
						self->it_state = LINEFOLLOW_READ_DATA_ERROR;
					}
					self->rx_frame.header_1 = LINEFOLLOW_FRAME_HEADER1;
					return -1;
			}
			
			case LINEFOLLOW_RECV_STARTBYTE_2: {
					self->rx_state = LINEFOLLOW_FRAME_HEADER2 == rx_byte ? LINEFOLLOW_RECV_COMMAND : LINEFOLLOW_RECV_STARTBYTE_2;
					if(self->rx_state == LINEFOLLOW_RECV_STARTBYTE_2)
					{
						self->it_state = LINEFOLLOW_READ_DATA_ERROR;
					}
					self->rx_frame.header_2 = LINEFOLLOW_FRAME_HEADER2;
					return -2;
			}
			
			case LINEFOLLOW_RECV_COMMAND: {
					self->rx_frame.elements.command = rx_byte;
					self->rx_args_index = 0;
					self->rx_state = LINEFOLLOW_RECV_LENGTH; 
					return 1;
			}
			
			case LINEFOLLOW_RECV_LENGTH: {
		/* 包长度超过允许长度 */
					if(rx_byte > 16) {
						self->rx_state = LINEFOLLOW_RECV_STARTBYTE_1; 
						self->it_state = LINEFOLLOW_READ_DATA_ERROR;
						return -3;
					}
					self->rx_frame.elements.length = rx_byte;
					self->rx_state = LINEFOLLOW_RECV_ARGUMENTS;
					return 2;
			}
	 
			case LINEFOLLOW_RECV_ARGUMENTS: {
					self->rx_frame.elements.args[self->rx_args_index++] = rx_byte;
					if (self->rx_args_index == self->rx_frame.elements.length) {
							self->rx_state = LINEFOLLOW_RECV_CHECKSUM;
					}
					return 3;
			}
			
			case LINEFOLLOW_RECV_CHECKSUM: {
				
					if(LineFollow_checksum((uint8_t*)&self->rx_frame) != rx_byte) {
							self->rx_state = LINEFOLLOW_RECV_STARTBYTE_1;
							self->it_state = LINEFOLLOW_READ_DATA_ERROR;
							return -99;
					} else {
							self->rx_state = LINEFOLLOW_RECV_STARTBYTE_1;
							memcpy(self->results, self->rx_frame.elements.args, sizeof(self->results));
							self->manual_mode = LINEFOLLOW_MODE_MANUAL_NULL;
							return 0;
					}
			}

			default: {
					self->rx_state = LINEFOLLOW_RECV_STARTBYTE_1;
					self->it_state = LINEFOLLOW_READ_DATA_ERROR;
					return -100;
			}
		}
	}
}

#endif
