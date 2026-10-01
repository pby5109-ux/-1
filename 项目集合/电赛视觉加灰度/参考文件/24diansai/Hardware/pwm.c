#include "pwm.h"

#define PWM_MAX 800
#define PWM_MIN -800

void set_pwm(uint16_t set_x,uint16_t set_y)
{
	if((set_x-1500)>PWM_MAX)
		set_x=PWM_MAX;
	if((set_x-1500)<PWM_MIN)
		set_x=-PWM_MIN;
	if((set_y-1280)>PWM_MAX)
		set_y=PWM_MAX;
	if((set_y-1280)<PWM_MIN)
		set_y=-PWM_MIN;
	
		DL_TimerG_setCaptureCompareValue(PWM_duoji_INST,set_x,GPIO_PWM_duoji_C1_IDX);
		DL_TimerG_setCaptureCompareValue(PWM_duoji_INST,set_y,GPIO_PWM_duoji_C0_IDX);
		
}