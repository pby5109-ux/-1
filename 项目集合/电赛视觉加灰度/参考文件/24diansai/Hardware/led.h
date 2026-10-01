#ifndef LED_H
#define LED_H

#include "main.h"

// 安全宏定义：使用 do-while(0) 结构确保语法一致性
#define LED1(x) do { \
    if (x) { \
        DL_GPIO_setPins(LED_PORT, DL_GPIO_PIN_2); \
    } else { \
        DL_GPIO_clearPins(LED_PORT, DL_GPIO_PIN_2); \
    } \
} while (0)

#define BEEP(x) do { \
    if (x) { \
        DL_GPIO_setPins(BEEP_PORT, BEEP_PIN_0_PIN); \
    } else { \
        DL_GPIO_clearPins(BEEP_PORT, BEEP_PIN_0_PIN); \
    } \
} while (0)

#define LED2(x) do { \
    if (x) { \
        DL_GPIO_setPins(LED_PORT, DL_GPIO_PIN_3); \
    } else { \
        DL_GPIO_clearPins(LED_PORT, DL_GPIO_PIN_3); \
    } \
} while (0)
void led1_toggle();
void led2_toggle();
#endif 