#include "led.h"

void led1_toggle()
{
 DL_GPIO_togglePins(LED_PORT,DL_GPIO_PIN_2);
}
void led2_toggle()
{
 DL_GPIO_togglePins(LED_PORT,DL_GPIO_PIN_3);
}
