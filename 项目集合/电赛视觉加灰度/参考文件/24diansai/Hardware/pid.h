#ifndef _pid_h
#define _pid_h

#include "main.h"



extern int16_t deer_pwm;
void Pid_Init(void);


struct FPID{
        float Set;             //设定值
        float Actual;          //实际值
        float err;             //当前误差
        float err_last;        //上一次误差
        float err_last_last;   //上上一次误差
        float last_derivative; //上次误差与上上次误差之差

        float Kp,Ki,Kd,Kout;
        float voltage;         //计算值
        float integral;        //误差积分值
        float GKD;             //陀螺仪系数
};

struct PID{
        int Set;             //设定值
        int Actual;          //实际值
        int err;             //当前误差
        int err_last;        //上一次误差
        int err_last_last;   //上上一次误差
        int last_derivative; //上次误差与上上次误差之差

        int Kp,Ki,Kd,Kout;
        int voltage;         //计算值
        int integral;        //误差积分值
};
extern struct FPID XPid;
extern struct FPID YPid;
extern struct FPID MotorL;//速度环
extern struct FPID MotorR;
extern struct FPID deer;//转向环
extern struct FPID loca;//juli环
int32_t loca_pid(float a,float b);
int32_t Xs_pid(float a,float b);
int32_t Ys_pid(float a,float b);
int32_t MotorL_pid(float a,float b);
int32_t MotorR_pid(float a,float b);
int32_t deer_pid(float a,float b);
int32_t position_pid(float a,float b);
#endif


