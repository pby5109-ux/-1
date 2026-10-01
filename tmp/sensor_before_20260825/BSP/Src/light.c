//
// Created by keysk on 2025/11/20.
//

#include "light.h"

#define COMMAND_MODE  0x10
#define ADDRESS  0x46
#define SEND_LEN  1
#define RECEIVE_LEN  2
// 转为十进制的数字
int power(uint8_t base, uint8_t index) {
  int result = 1;
  if (index == 0) {
    return 1;
  }
  for (uint8_t i = 0; i < index; i++) {
    result *= base;
  }
  return result;
}
// 传感器分辨率为1-65535,计算获取光照值
uint16_t Light_Get(void) {
  uint8_t command_data = COMMAND_MODE;
  uint8_t receive_light_data[2] = {0};
  if (I2C_WriteData(ADDRESS, &command_data,SEND_LEN) == 0) {
    if (I2C_ReadDate(ADDRESS, receive_light_data,RECEIVE_LEN) == 0) {
      uint16_t light_result = 0;
      const uint16_t combined_data = (receive_light_data[0] << 8) | receive_light_data[1];
      for (uint8_t i = 0; i < 16; i++) {
        if (((combined_data >> i) & 0x01) == 1) {
          light_result += power(2, i);
        }
      }
      return (uint16_t)(light_result / 1.2);
    }
  }
  return 0;
}
