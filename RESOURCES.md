# 四项目嵌入式面试准备 Resources

## Knowledge

- `记忆与产物/05-面试题库/四项目嵌入式面试完整题库.md`
  四项目唯一完整题库，包含A/B/C分级、折叠答案、追问、错误点、证据、贡献边界、计算速查和未确认清单。当前题量、节点题号和接续状态见`记忆与产物/00-项目接续记忆.md#track-bank`，此处不维护版本副本。
- `记忆与产物/03-知识资料/新增项目源码全景-传感器终端与电赛小车.md`
  两个项目已经由源码、配置、构建产物和本地手册核对的事实基线。用于所有项目问题、引脚、数据流和缺陷判断。
- `D:\APP\project_practice\sensor_project\sensor.design`
  传感器终端唯一源码。历史提交`d46bd46`新增LoRaDebug软件变体、协议层和节点状态机；`59bc46b`新增在线PC串口网关、流式组帧、动态ACK、有界去重和CSV日志。用于裸机循环、UART DMA、RTC Stop和LoRa教学；当前分支及远端状态须现场核对，不沿用旧的“尚未推送”表述。
- `低功耗项目理解产物/04-2026-08-27-源码支撑的低功耗LoRa一日教学总纲.md`
  8月27日课程顺序、代码证据、验收线和RF未实测边界。
- `低功耗项目理解产物/08-LoRa剩余知识总览-无线参数可靠性故障与验收.html`
  用户停止逐题教学后生成的完整阅读资料，覆盖模块预配置、LEVEL/BW/SF/CR/功率、ACK状态机、多节点、RSSI、故障树、实物测试和面试表达。
- `lessons/0004-lora-from-zero-implementation.html`
  从两个模块透明对传开始，逐步加入STM32 UART、M0/M1/AUX、18B协议、DMA、ACK、网关和RTC Stop，并解释现有LoRa函数的职责、变量生命周期与两层重试。
- [大夏龙雀DX-LR22-433T22D技术手册](https://www.szdx-smart.com/static/upload/2025/12/08/202512086979.pdf)
  LLCC68串口模块的引脚、电平、功耗、AUX高忙低完成及M0/M1模式的一手依据。
- [大夏龙雀DX-LR22-433T22D串口应用指导](https://www.szdx-smart.com/static/upload/2025/12/11/202512113214.pdf)
  `AT+SWITCH=1`、透明/定点/广播、速率等级和模式切换的一手依据。
- [LoRa Alliance：What is LoRaWAN](https://lora-alliance.org/about-lorawan/)
  区分LoRa物理层、自定义点对点协议与LoRaWAN网络协议。
- [ST RM0008：STM32F1参考手册](https://www.st.com/resource/en/reference_manual/cd00171190-stm32f101-103-105-107-stm32f100-series-armbased-32bit-mcus-stmicroelectronics.pdf)
  RTC、PWR、RCC、Stop进入/退出条件与退出后HSI作为系统时钟的一手依据。
- [ST AN2629：STM32F101/102/103低功耗模式](https://www.st.com/resource/en/application_note/an2629-stm32f101xx-stm32f102xx-and-stm32f103xx-lowpower-modes-stmicroelectronics.pdf)
  Sleep/Stop/Standby差异、稳压器模式、唤醒延迟和功耗测试注意事项的一手依据。
- `C:\Users\彭\OneDrive\Desktop\各类外设参考手册\温湿度传感器AHT20数据手册-728a6f02fca5b1794f436ec100ef50ac.pdf`
  AHT20 V1.0本地手册。表2给出休眠/测量电流，图6/7给出休眠电流随温度/VDD变化，表10确认Busy Bit7=0时设备空闲并处于休眠状态；用于纠正“无显式Sleep函数就没有低功耗”的错误推断。
- `D:\APP\project_practice\电赛_project\24diansai`
  电赛小车唯一源码。用于按键/OLED、五路GPIO循迹和MSPM0生成配置教学。
- [TI: MSPM0G350x datasheet](https://www.ti.com/lit/ds/symlink/mspm0g3507.pdf)
  芯片内核、80MHz能力和外设边界的一手来源；用于MSPM0基础事实。
- [TI: MSPM0 G-Series 80MHz Technical Reference Manual](https://www.ti.com/lit/ug/slau846a/slau846a.pdf)
  时钟、TimerA/TimerG、GPIO和NVIC相关硬件行为的一手来源；只查课程相关章节。
- [TI: MSPM0 DriverLib Overview](https://software-dl.ti.com/msp430/esd/MSPM0-SDK/latest/docs/english/driverlib/Driverlib_Overview.html)
  解释DriverLib为何是寄存器之上的外设API层，以及与当前`DL_`调用的关系。
- [TI: Using SysConfig with MSPM0](https://software-dl.ti.com/msp430/esd/MSPM0-SDK/2_10_00_04/docs/chinese/tools/sysconfig_guide/doc_guide/doc_guide-srcs/sysconfig_guide_CN.html)
  解释`.syscfg`如何配置引脚/外设并生成C头文件和源文件，及Keil集成边界。
- [TI: MSPM0G1X0X/G3X0X GPIO DriverLib API](https://software-dl.ti.com/msp430/esd/MSPM0-SDK/2_04_00_06/docs/chinese/driverlib/mspm0g1x0x_g3x0x_api_guide/html/group___g_p_i_o.html)
  用于确认`DL_GPIO_readPins()`返回位掩码而不是抽象布尔值。
- [乐鑫科技当前校园招聘](https://www.espressif.com/zh-hans/join-us/job-search?field_job_classification_tid=All&field_job_location_select_tid%5B0%5D=111&page=6&title=)
  当前Wi-Fi/BLE/应用方案嵌入式岗位对C/C++、RTOS、系统调试、无线协议以及性能/功耗/内存优化的要求，用于秋招方向判断。
- [Telink校园招聘](https://www.telink-semi.cn/campus-recruitment)
  当前无线SoC嵌入式岗位覆盖低功耗管理、GPIO/UART/SPI/I2C/PWM/ADC、FreeRTOS/Zephyr和BLE/Zigbee/Thread/Matter/Wi-Fi，用于IoT固件能力画像。
- [海尔当前嵌入式岗位](https://maker.haier.net/client/job/detail/id/10229087/recommend_record/1)
  2026年岗位覆盖MCU/DSP驱动、ADC/DAC/PWM与常用总线、软硬件联调、RTOS和低功耗预研，用于验证通用固件岗位的共同基础。
- [大疆2027校园招聘](https://careers.dji.com/zh-CN/campus?source=RM-Title)
  2027届秋招已于2026-06-25开启且招满即止，用于确认当前应并行投递和准备面试，不能等项目全部学习完再开始。
- [中电港嵌入式与电机电控岗位](https://cn.linkedin.com/jobs/view/%E5%B5%8C%E5%85%A5%E5%BC%8F%E4%B8%8E%E7%94%B5%E6%9C%BA%E7%94%B5%E6%8E%A7%E7%B3%BB%E7%BB%9F%E5%B7%A5%E7%A8%8B%E5%B8%88-j17206-at-%E4%B8%AD%E7%94%B5%E6%B8%AFcecport-4425711761)
  当前运动控制岗位进一步要求BLDC/FOC、RTOS和CAN/EtherCAT，用于说明五路循迹与专业电机控制岗位之间的能力距离；这是单个岗位样本，不代表全部市场。

### OLED按需显示与供电域参考

- [TI TPS22919](https://www.ti.com/product/TPS22919)：高边负载开关、受控上升沿、关断电流和输出放电边界。
- [AOS AO3401A数据手册](https://www.aosmd.com/res/data_sheets/AO3401A.pdf)：3.3V场景P-MOS高边原型，按VGS和RDS(on)而非只看阈值电压选型。
- [TI TMUX1121/1122/1123数据手册](https://www.ti.com/lit/ds/symlink/tmux1122.pdf)：双SPST信号开关；1121高使能、1122低使能，不可混接。
- [TI：断电保护与反向供电](https://www.ti.com/document-viewer/lit/html/SCDA015)：信号路径高阻、ESD倒灌及开关自身供电前提。
- `低功耗项目理解产物/01-低功耗系统设计决策与实施边界.md`第13节和同目录`0001-整机低功耗从Stop到蓝牙.html#oled-on-demand`：按键查看、软件关屏与硬断电的取舍、共享I²C隔离和RTC期限。
- 本地CH1116手册第33页：`C:\Users\彭\OneDrive\Desktop\各类外设参考手册\OLED驱动芯片手册_CH1116-defbfae74f48bf57105d60d9d097c386.pdf`，确认0xAE/0xAF及0xAD、0x8A/0x8B命令。

## Wisdom (Communities)

- 暂不安排外部社区。当前目标是一天内围绕真实源码建立可检验的面试回答，实物波形、调试器观察和用户本人项目经历优先于论坛经验。

## Gaps

- 用户已确认实际经历为2025年控制类电赛；当前`24diansai/2024TiCup`目录是2024代码参考，2025年继续使用同一套循迹实现。确切赛题名称、任务书和最终现场成绩仍未在工程目录中找到，涉及这些细节时由用户或证书/原题补充，不从目录名猜测。
- `datafun()`状态机的个人作者边界无法由源码元数据确定，后续继续按用户声明的有限贡献表述。
