#include "LineFollow.h"
#include "usart.h"
#include "string.h"

LineFollowHandleTypeDef LineFollow;

static int8_t LineFollow_write_and_read(LineFollowHandleTypeDef *self, uint8_t cmd, bool tx_only)
{
  int8_t ret = -1;	
	switch(self->it_state)
	{
		case LINEFOLLOW_WRITE_DATA_READY:
			if(cmd == LINEFOLLOW_CMD_NULL && tx_only == false){
				self->tx_byte_index = 1;
				memcpy(&self->tx_frame, &cmd, sizeof(cmd));
				__HAL_UART_ENABLE_IT(&huart2, UART_IT_RXNE);
			}else{
				memcpy(&self->tx_frame, &cmd, sizeof(cmd));
				self->tx_byte_index = 0;
				self->tx_only = tx_only;
				self->rx_state = LINEFOLLOW_RECV_STARTBYTE_1;
				__HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_RXNE);
				__HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_TC);
				__HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_TXE);
				
				__HAL_UART_ENABLE_IT(&huart2, UART_IT_TXE);
				__HAL_UART_ENABLE_IT(&huart2, UART_IT_TC);
			}
		
			ret = 1;
			break;
		
		case LINEFOLLOW_READ_DATA_FINISH:
			self->it_state = LINEFOLLOW_WRITE_DATA_READY;
			ret = 0;
			break;
		
		case LINEFOLLOW_READ_DATA_ERROR:
			self->it_state = LINEFOLLOW_WRITE_DATA_READY;
			break;
			
		default:
			break;
	}
	return ret;
}



void LineFollowUART_init(uint8_t Mode)
{
		memset(&LineFollow, 0, sizeof(LineFollow));
    __HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_TXE);
    __HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_TC);
    __HAL_UART_CLEAR_FLAG(&huart2, UART_FLAG_RXNE);
		LineFollow.work_mode = Mode;
		LineFollow_write_and_read(&LineFollow, LineFollow.work_mode, true);
		LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
}

bool LineFollowUART_State(LineFollowHandleTypeDef* State)
{
	if(LineFollow.work_mode == LINEFOLLOW_MODE_MANUAL)
	{
		LineFollow.manual_mode = LINEFOLLOW_MODE_MANUAL_STATE;
		if (0 == LineFollow_write_and_read(&LineFollow, LINEFOLLOW_MODE_MANUAL_STATE, false)) 
		{
			for(int i=0; i<sizeof(LineFollow.data);i++){
				State->data[i] = (LineFollow.results[0] >> i) & 0x01;
			}
			LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
			return true;
		}
	}
	else
	{
		if (0 == LineFollow_write_and_read(&LineFollow, LINEFOLLOW_CMD_NULL, false)) 
		{
			for(int i=0; i<sizeof(LineFollow.data);i++){
				State->data[i] = (LineFollow.results[0] >> i) & 0x01;
			}
			LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
			return true;
		}
	}
	
	return false;
}

bool LineFollowUART_Analog(LineFollowHandleTypeDef* Analog)
{
	uint8_t count = 0;
	if(LineFollow.work_mode == LINEFOLLOW_MODE_MANUAL)
	{
		LineFollow.manual_mode = LINEFOLLOW_MODE_MANUAL_ANALOG;
		if (0 == LineFollow_write_and_read(&LineFollow, LINEFOLLOW_MODE_MANUAL_ANALOG, false)) 
		{
			for(int i=0; i<sizeof(LineFollow.data);i++){
				Analog->data[i] = LineFollow.results[count] | (LineFollow.results[count+1] << 8);
				count += 2;
			}
			LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
			return true;
		}
	}
	else
	{
		if (0 == LineFollow_write_and_read(&LineFollow, LINEFOLLOW_CMD_NULL, false)) 
		{
			for(int i=0; i<sizeof(LineFollow.data);i++){
				Analog->data[i] = LineFollow.results[count] | (LineFollow.results[count+1] << 8);
				count += 2;
			}
			LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
			return true;
		}
	}
	
	return false;
}

bool LineFollowUART_Threshold(LineFollowHandleTypeDef* Threshold)
{
	uint8_t count = 0;
	if(LineFollow.work_mode == LINEFOLLOW_MODE_MANUAL)
	{
		LineFollow.manual_mode = LINEFOLLOW_MODE_MANUAL_THRESHOLD;
		if (0 == LineFollow_write_and_read(&LineFollow, LINEFOLLOW_MODE_MANUAL_THRESHOLD, false)) 
		{
			for(int i=0; i<sizeof(LineFollow.data);i++){
				Threshold->data[i] = LineFollow.results[count] | (LineFollow.results[count+1] << 8);
				count += 2;
			}
			LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
			return true;
		}
	}
	else
	{
		if (0 == LineFollow_write_and_read(&LineFollow, LINEFOLLOW_CMD_NULL, false)) 
		{
			for(int i=0; i<sizeof(LineFollow.data);i++){
				Threshold->data[i] = LineFollow.results[count] | (LineFollow.results[count+1] << 8);
				count += 2;
			}
			LineFollow.it_state = LINEFOLLOW_WRITE_DATA_READY;
			return true;
		}
	}
	
	return false;
}

