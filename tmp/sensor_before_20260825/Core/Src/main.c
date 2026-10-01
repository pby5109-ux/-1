/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "i2c.h"
#include "rtc.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "string.h"
#include "stdio.h"
#include "font.h"
#include "aht20.h"
#include "oled.h"
#include "light.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
extern RTC_HandleTypeDef hrtc;           /* RTC句柄（定义在 rtc.c） */
volatile uint8_t rtc_alarm_wakeup = 0;   /* RTC闹钟唤醒标志 */
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
static void Enter_Stop_Mode(uint32_t seconds); /* 进入 Stop 模式，seconds 后唤醒 */
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
float temp=0;//温度
int humi=0;//湿度
int light=0;//光照
char oled_buf[50];   // 专用于屏幕显示的数组
char uart_buf[60];   // 专用于串口 DMA 发送的数组（适当放大防止溢出）
uint8_t read_flag=0;//读取标志
int timenow=0;//当前时间

/**
 * @brief  进入 Stop 低功耗模式，seconds 秒后由 RTC 闹钟唤醒
 * @param  seconds  睡眠秒数
 *
 * F103 RTC 特点：
 *   - 32位自由计数器，LSE 32.768kHz / (AsynchPrediv+1) = 1Hz
 *   - 闹钟寄存器 = 绝对计数值（当前值 + seconds）
 *   - 闹钟中断经 EXTI Line 17 路由到 NVIC
 *
 * 流程：
 *   1. 读取当前 RTC 计数值，计算闹钟目标值
 *   2. 写入 RTC 闹钟寄存器并使能中断
 *   3. 暂停 SysTick（防止 SysTick 中断立即唤醒）
 *   4. 进入 Stop 模式（WFI 挂起）
 *   5. 唤醒后重启 PLL/时钟，恢复 SysTick
 */
static void Enter_Stop_Mode(uint32_t seconds)
{
    /* --- 1. 设置 RTC 闹钟 --- */
    /* F103 没有 HAL_RTCEx_GetSecond，直接读 RTC 计数寄存器 */
    uint32_t cnt = (uint32_t)(RTC->CNTH << 16) | RTC->CNTL;
    uint32_t alarm_val = cnt + seconds;

    /* 等待 RTC 上一次写操作完成（RTOFF=1） */
    while (__HAL_RTC_ALARM_GET_FLAG(&hrtc, RTC_FLAG_RTOFF) == RESET);

    /* 进入 RTC 配置模式 */
    SET_BIT(RTC->CRL, RTC_CRL_CNF);
    /* 写入闹钟寄存器（高16位 + 低16位） */
    WRITE_REG(RTC->ALRH, (alarm_val >> 16) & 0xFFFF);
    WRITE_REG(RTC->ALRL,  alarm_val        & 0xFFFF);
    /* 退出配置模式 */
    CLEAR_BIT(RTC->CRL, RTC_CRL_CNF);
    /* 等待写完成 */
    while (__HAL_RTC_ALARM_GET_FLAG(&hrtc, RTC_FLAG_RTOFF) == RESET);

    /* 使能 RTC 闹钟中断 + EXTI Line17（RTC Alarm 唤醒线） */
    __HAL_RTC_ALARM_ENABLE_IT(&hrtc, RTC_IT_ALRA);
    __HAL_RTC_ALARM_EXTI_ENABLE_IT();
    __HAL_RTC_ALARM_EXTI_ENABLE_RISING_EDGE();

    /* --- 2. 清除唤醒标志 --- */
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    rtc_alarm_wakeup = 0;

    /* --- 3. 暂停 SysTick（Stop 模式下 SysTick 仍在计时会立即唤醒） --- */
    HAL_SuspendTick();

    /* --- 4. 进入 Stop 模式（低功耗调压器，WFI 等待中断） --- */
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);

    /* ===== CPU 从此处被唤醒 ===== */

    /* --- 5. 重新配置系统时钟（Stop 唤醒后自动回退到 HSI，需重启 PLL） --- */
    SystemClock_Config();

    /* --- 6. 恢复 SysTick --- */
    HAL_ResumeTick();

    /* --- 7. 清除 RTC 闹钟标志和 EXTI 挂起位 --- */
    __HAL_RTC_ALARM_CLEAR_FLAG(&hrtc, RTC_FLAG_ALRAF);
    __HAL_RTC_ALARM_EXTI_CLEAR_FLAG();
    __HAL_RTC_ALARM_DISABLE_IT(&hrtc, RTC_IT_ALRA);
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_I2C1_Init();
  MX_USART3_UART_Init();
  MX_RTC_Init();
  /* USER CODE BEGIN 2 */
  HAL_Delay(20);
  OLED_Init();
  AHT20_Init();
  /* 释放软件 I2C 总线（PA10 SDA, PA11 SCL 确保空闲高电平） */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_10|GPIO_PIN_11, GPIO_PIN_SET);
  HAL_Delay(10);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* 1. 采集温湿度光照数据 */
    AHT20_Measure();
    temp = AHT20_Temperature();
    humi = AHT20_Humidity();
    light = Light_Get();

    /* 2. OLED 显示 */
    OLED_NewFrame();
    sprintf(oled_buf, "温度=%.1f℃ ", temp);
    OLED_PrintString(0, 0, oled_buf, &font16x16, OLED_COLOR_NORMAL);
    sprintf(oled_buf, "湿度=%d%%", humi);
    OLED_PrintString(0, 20, oled_buf, &font16x16, OLED_COLOR_NORMAL);
    sprintf(oled_buf, "光照=%d lx", light);
    OLED_PrintString(0, 40, oled_buf, &font16x16, OLED_COLOR_NORMAL);;
    OLED_ShowFrame();

    /* 3. 串口发送（必须等 DMA 发完再进 Stop，否则 UART 时钟关闭后数据丢失） */
    // sprintf(uart_buf, "温度：%.1f℃  湿度：%d%%\r\n 光照：%d lx", temp, humi, light);
    if (temp>=25.0&&temp<=35.0&&humi>=45&&humi<=70&&light>=1000)
    {
      sprintf(uart_buf, "normal temp=%.1f C humi=%d%% l=%d lx\r\n", temp, humi, light);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, GPIO_PIN_SET);
    }
    else
    {
      sprintf(uart_buf, "warning temp=%.1f C humi=%d%% l=%d lx\r\n", temp, humi, light);
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_7, GPIO_PIN_RESET);
    }
    // sprintf(uart_buf, "temp %.1f c humi %d%%  light %d lx\r\n", temp, humi, light);//手机接收
    HAL_UART_Transmit_DMA(&huart3, (uint8_t*)uart_buf, strlen(uart_buf));
    /* DMA 是非阻塞的！必须阻塞等到发送完成再进 Stop */
    while (HAL_UART_GetState(&huart3) != HAL_UART_STATE_READY)
    {
        __NOP();  /* 空转等待 DMA 传输完成 */
    }

    /* 4. 进入 Stop 低功耗模式，5 秒后 RTC 闹钟唤醒
     *    修改 Enter_Stop_Mode(5) 的参数即可调整睡眠时长 */
    Enter_Stop_Mode(5);

    /* 唤醒后继续循环（SystemClock 已在 Enter_Stop_Mode 内重新配置好） */
    }
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */

  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE|RCC_OSCILLATORTYPE_LSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.LSEState = RCC_LSE_ON;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_RTC;
  PeriphClkInit.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
