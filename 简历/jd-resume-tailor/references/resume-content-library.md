# 已确认简历素材池

> 2026-09-18：新投递先按[current-workflow.md](current-workflow.md)核对动态模板，JSON仅为快照，不覆盖新模板。四项目全部保留，默认仪器＋节点＋MSPM0/K230瞄准，智慧农场按JD可替换入选。以下历史稿不覆盖后期已核验定稿；第3节为农场素材，第7节为校园长版。实习写/不写、校园长/短/无独立选择。下方旧固定8条及组合建议不再约束新稿。

本文保存可直接改写的候选文字。每次仍需结合JD重排和压缩，并在`approved-content.json`中记录对应证据ID。

## 1. 专业技能

### embedded母版

- `开发调试`：使用Keil、STM32CubeMX、VS Code、CLion、CMake/GCC、OpenOCD和Git；能结合原理图、芯片手册、ST-Link、示波器及万用表定位软硬件问题。`skill.toolchain, skill.debug_tools`
- `RTOS外设`：完成过FreeRTOS移植及`FreeRTOSConfig.h`项目配置，熟悉任务调度及队列、事件组、信号量、互斥锁、软件定时器；使用过UART/I²C/SPI、ADC/DAC/DMA、TIM/PWM/RTC/EXTI等常用外设。`skill.rtos, skill.peripherals, instrument.freertos_port`
- `编程及技能`：熟悉C语言、STM32F103/HAL及TI MSPM0G3507 DriverLib，理解指针、结构体、位运算、动态内存及static/const/volatile；CET-4、C1驾驶证，使用WPS/Office整理技术文档。`skill.c, skill.mcu, skill.docs`

### general母版

- `工程协作`：使用Keil、STM32CubeMX、VS Code、CLion、CMake/GCC、OpenOCD和Git完成工程构建与调试；使用WPS/Office整理测试记录、技术材料和汇报文档；CET-4、C1驾驶证。`skill.toolchain, skill.docs`
- `测试验证`：能够结合需求、原理图和芯片手册制定排查顺序，使用ST-Link、示波器、万用表及串口工具完成信号测试、功能验证和问题定位。`skill.debug_tools, profile.strengths`
- `专业基础`：熟悉C语言、STM32F103、FreeRTOS以及UART/I²C/SPI、ADC/DMA/PWM等常用外设，具备嵌入式模块开发和软硬件联调基础。`skill.c, skill.mcu, skill.rtos, skill.peripherals`

Python默认不写。只有JD明确需要、预览说明为条件能力且用户同意时，可加入“了解Python基础，可阅读和修改简单串口数据处理脚本”。

## 2. 综合电子测量平台

项目头：`基于STM32与FreeRTOS的综合电子测量平台｜核心开发与系统调试｜2026.03—2026.06`

- `系统架构`：在STM32F103RCT6上完成FreeRTOS移植及`FreeRTOSConfig.h`项目配置，搭建集示波采集、数字万用表、信号发生器及稳压电源输出监测于一体的综合测量平台；采用BSP/GUI/TASK分层，通过事件组按区域刷新、单槽覆盖队列传递最新测量值，并以二值信号量同步SPI DMA传输完成。`instrument.scope, instrument.architecture, instrument.freertos_port`
- `示波采集`：构建比较器—EXTI—TIM3 TRGO—ADC1—DMA采集链，最高配置500 kSa/s采集1024点；结合10 ms Hold-Off、100 ms强制触发及Auto/One-Shot状态控制，完成触发窗口管理、无信号兜底与单帧冻结。`instrument.oscilloscope_chain, instrument.trigger_modes`
- `测量输出`：采用ADC1注入组以10 Hz周期采集DMM输入、VREFINT、稳压输出和触发阈值，基于VREFINT反推VDDA并结合GPIO档位识别完成多量程换算；通过TIM5 TRGO驱动DAC+DMA循环输出波形，动态调整采样率与有效点数，并解决低频档定时参数未更新及频率切换滞后一档问题。`instrument.dmm_vref, instrument.awg_waveform, instrument.awg_debug`

不得把最后一条改为“三角波”或“三种波形”，除非当前唯一源码重新核验已经形成上升/下降三角表并有编译、烧录、示波器验证证据。

## 3. 智慧农场

项目头：`基于STM32与FreeRTOS的智慧农场环境监测与控制系统｜核心开发与系统优化｜2025.07—2025.09`

- `任务架构`：基于STM32F103C8T6与FreeRTOS搭建环境监测和自动控制系统，将传感采集、按键/编码器、OLED显示和BLE通信划分为Sensor、Input、Screen、BLE四个任务，并以farmState/farmSafeRange解耦实时状态、界面显示与可配置安全阈值。`farm.architecture`
- `数据采集`：结合AHT20、BH1750及土壤/雨滴传感器采集空气温湿度、土壤温湿度、光照和降雨相对数据，使用ADC1扫描与循环DMA、ADC2连续转换及I²C完成多源读取；以互斥锁保护AHT20与OLED共享的I²C1总线。`farm.sensors, farm.i2c_mutex, farm.sensor_calibration`
- `控制告警`：基于阈值驱动水泵和PWM风扇，通过指针消息队列与UART DMA发送JSON告警；修复队列满时动态消息未释放造成的内存泄漏，将持续报警改为warning/recovered状态边沿，并为水泵加入5%滞回，减少重复消息与临界启停。`farm.queue_ownership, farm.alert_state, farm.hysteresis`

AHT20“两段事务＋osDelay”只能写成设计方案，不进入完成式正文；当前版本也不主动写蜂鸣器已启用。

## 4. 低功耗LoRa环境传感节点

> 2026-09-04确认：该项目用于证明低功耗调度和可靠通信能力，传感采集只作为场景背景，避免与智慧农场重复。三条详细版与两条压缩版均已获用户认可；前者用于低功耗/无线/协议岗位，后者用于通用嵌入式岗位或一页空间受限时。默认正文写“主机侧协议测试”，不主动突出Python。9月8日已核对OLED/雨滴供电与双期限代码，新增候选见下；BH1750单次模式仍只作设计追问。详细证据见`project-evidence.json`的`lora_node`。

项目头：`基于STM32的低功耗LoRa环境传感节点｜独立开发｜2025.11—2026.01`

### 两条版（已确认，通用/一页压缩）

- `低耗调度`：面向环境状态的周期采集上报，基于RTC Alarm—EXTI17构建Stop休眠唤醒链，唤醒后恢复PLL与72 MHz系统时钟，并按传感状态选择正常30秒、异常10秒休眠。`lora.independent_integration, lora.stop_cycle, lora.periods`
- `可靠通信`：基于USART3 DMA与LoRa设计18字节遥测帧、CRC16-CCITT校验、ACK匹配及一次整帧重试；编写PC串口网关处理半帧/粘帧、错误重同步与重复帧，并完成主机侧协议测试。`lora.tx_lifecycle, lora.protocol, lora.gateway, lora.software_verification`

### 三条版（已确认，低功耗/无线/协议JD）

- `低耗调度`：面向温湿度、光照与雨滴状态的周期采集上报，构建RTC Alarm—EXTI17—Stop休眠唤醒链，进入Stop前暂停SysTick，唤醒后恢复PLL与72 MHz系统时钟；根据传感有效性及阈值状态选择正常30秒、异常10秒休眠。`lora.independent_integration, lora.stop_cycle, lora.periods`
- `可靠通信`：基于USART3 DMA实现LoRa数据上报，设计18字节大端遥测帧、CRC16-CCITT、valid/alert及节点ID/序号匹配ACK；通过有限等待、一次整帧重试和同序号重发，避免故障路径无限占用活动时间。`lora.tx_lifecycle, lora.protocol`
- `网关验证`：编写在线PC串口网关处理半帧、粘帧、错误重同步及重复帧，支持动态ACK和CSV记录；完成主机侧协议测试，覆盖帧编解码、CRC异常拒绝、串口分包及重复包处理。`lora.gateway, lora.software_verification`

### 技能区替换素材（按JD选择，不额外增加第四条技能）

- `低耗通信`：使用RTC/Stop实现周期唤醒及系统时钟恢复；具备UART DMA、定长帧/CRC、ACK匹配、超时重试与串口流式解析的项目实践。`lora.stop_cycle, lora.tx_lifecycle, lora.protocol, lora.gateway`

这是MCU低功耗机制与通信软件经历，不等于已完成整板电源域设计或量化优化；默认简历不因网关和测试代码而单列Python技能，仍遵守`skill.python`边界。

### 9月8日新增候选（已核对代码，未批准替换投递稿）

- `外设节能`：编写OLED按键查看、30秒到期关闭及供电/共享I²C支路隔离控制，配合雨滴模块上电稳定、8次采样后断电；新增硬件链待上板验证。`lora.oled_power_code, lora.rain_power_code`
- `期限调度`：基于RTC分别管理采样与显示到期期限，选择较早期限进入Stop，按键唤醒不重置采样期限，并在唤醒后恢复系统时钟；新增调度硬件时序待实测。`lora.dual_deadline_code, lora.stop_cycle`

仅在JD确实需要时替换低耗调度条目，不把四个低功耗条目全部塞入一页；保留通信/网关的独立亮点。以上属于2026年9月后续迭代，选用前须在预览确认项目时间表达，不能放在2026.01结束的时间栏下暗示当时已完成。控制代码存在不等于外部开关已接好、无倒灌或省电比例达标。

### 保留的设计追问

BH1750单次测量后Power Down、LoRa计划引脚迁移仍未落实；最终SleepRadio返回值未检查。仅用作“现状—改进—验证方法”的面试题，不能填成已完成业绩。

### JD预览与追问钩子

- 低功耗岗位：突出RTC/Stop、时钟恢复和30/10秒策略；追问“为什么休眠30秒不等于严格30秒采样、MCU Stop为什么不等于整板省电”。要求电源域量化优化时标为`partial`控制代码经验与实测缺口，不当作已做业绩。
- 通信/可靠性岗位：突出valid与数值分离、UART完成/无线确认分离、有限重试及在线流式解析；追问“整帧重试与启动重试、重复ACK与恰好一次、网关先ACK后写日志”的边界。
- 既有主机测试仅验证Python端，C节点流程及RF仍待验证；最终`SleepRadio()`返回未检查，不写“保证模块休眠”或“所有故障均已闭环”。
- 不得写RF距离、RSSI、丢包率、实测功耗、LoRaWAN、远程阈值配置或已完成多节点组网；旧基础采集/RTC上板记录不能覆盖新增LoRa整链。保持预览确认后再生成的规则。

## 5. 控制类JD备用项目

项目头：`TI杯2025年全国大学生电子设计竞赛E题《简易自行瞄准装置》｜循迹与人机交互开发｜2025.07—2025.08`

- `循迹控制`：基于TI MSPM0G3507完成五路灰度传感器GPIO采集与5 bit状态编码，建立中心、偏移和转向状态的离散映射并输出循迹误差，协同接入团队PID与左右轮差速控制接口。`car_contest.contribution, car_contest.mapping, car_contest.team_context`
- `人机交互`：完成四键扫描与OLED多页面显示，支持任务模式、圈数及启停参数调整；配合电机、编码器和姿态模块完成团队功能联调。`car_contest.contribution, car_contest.team_context`

此项目只在控制/机器人/智能车JD中提升为详细项目。不得写当前源码编译通过、本人完成整套PID或竞赛获奖。

## 6. 企业实践

经历头：`烟台东方威思顿电气有限公司｜智能电表软硬件测试实习生｜2025.10—2025.11`

- `产品认知`：学习智能电表及用电信息采集终端的原理图、PCBA布局与主要元器件，梳理电源、采样、计量、通信和安全防护单元；结合IP68高防护电表案例理解密封结构设计。`experience.meter_training`
- `开发板实践`：参加电能表开发板软硬件讲解与上手操作，学习工况事件、远程费控和主动上报等功能，并围绕终端采集异常建立供电接线—信号输入—通信参数—软件逻辑的分层排查方法。`experience.meter_board`

不得补板卡型号、真实RS485故障闭环、测试数量或量产指标。

## 7. 校园、竞赛与自我评价

校园头：`山东建筑大学校学生会科创部｜部长｜2023.09—2025.06`

- `科创组织`：统筹约50名成员，参与组织电赛、西门子杯、蓝桥杯及国产MCU产品等校级宣讲，负责人员分工、跨部门协调、宣传物料、会场布置与流程安排，保障活动按计划落地。`campus.organization`
- `现场保障`：参与组织文艺晚会、校园歌手大赛等200余人活动，设置双麦克风及主备音响方案；音频设备突发故障后按预案切换备用设备，恢复现场声音并保障流程继续。`campus.event_recovery`

竞赛四行：

- `蓝桥杯`：第十六届全国软件和信息技术专业人才大赛单片机设计与开发大学组山东赛区三等奖（2025）。`award.lanqiao`
- `电子设计`：TI杯2025年全国大学生电子设计竞赛E题《简易自行瞄准装置》；基于TI MSPM0G3507负责按键/OLED交互与五路灰度循迹模块，完成状态编码、偏差映射及PID/差速控制接口联调。`car_contest.contribution, car_contest.team_context`
- `项目实践`：2025.05—2025.07担任STM32F103C8T6开放实验小车循迹小组负责人，完成五路灰度状态处理与误差接口，项目及个人验收优秀。`car_lab.contribution, car_lab.validation`
- `校级荣誉`：优秀共青团员｜优秀学生（个人）｜三好学生。`award.school`

自我评价：

- `个人优势`：具备MCU项目开发、软硬件联调与问题定位能力；做事认真负责，注重持续学习、团队协作和现场执行。`profile.strengths`

使用“MCU项目开发”比仅写“STM32项目开发”更适合非STM32专属JD，同时有STM32和MSPM0经历支撑。

## 8. 项目排序规则

- MCU/RTOS/外设：综合仪器→智慧农场→LoRa节点。
- 仪器/采集/测试：综合仪器→智慧农场→LoRa节点，提高企业实践权重。
- 低功耗/无线/IoT：LoRa节点→智慧农场→综合仪器；LoRa使用三条版，并从另一个项目压缩一条以保持总数8。
- 控制/机器人/智能车：综合仪器或智慧农场→电赛小车→LoRa/另一核心项目；电赛使用两条详细稿，并从竞赛栏移除重复的一行。
- 央国企/技术综合：三个核心项目默认不变，提高企业实践、测试验证、组织协调和文档能力权重。
