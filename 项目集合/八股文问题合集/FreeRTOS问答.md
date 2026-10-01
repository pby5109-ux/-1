# FreeRTOS 八股问答

记录规则：问题＋关键解答，保留机制、易错点和必要接口，后续持续追加。

## 1. 为什么软件定时器要设置队列长度？

- `configTIMER_QUEUE_LENGTH` 设置共享定时器命令队列的容量，单位为命令条数。
- 启动、停止、重置、修改周期等请求先入队，由定时器服务任务处理。
- 容量限制的是待处理命令数，不是定时器数量，也不是到期事件数量。
- 队列满时，任务侧接口可按指定时间等待；不等待或超时则发送失败。ISR 接口不能阻塞。
- 根据命令突发积压量设置；增大容量会增加 RAM 占用。

## 2. 软件定时器动态创建与静态创建有什么区别？

- 动态：`xTimerCreate()` 从 FreeRTOS 堆分配对象，内存不足可能返回 `NULL`。
- 静态：`xTimerCreateStatic()` 使用用户提供的 `StaticTimer_t` 缓冲区；每个定时器独立提供，使用期间必须有效，常用全局或 static 变量。
- 对应配置：`configSUPPORT_DYNAMIC_ALLOCATION`、`configSUPPORT_STATIC_ALLOCATION`。
- 两者运行机制相同，创建后都需要启动；静态指内存提供方式，创建接口仍在运行时执行。
- 删除命令处理后，动态对象内存按堆实现释放；静态缓冲区仍由用户管理。
- 对象缓冲区不是命令队列，也不是回调栈；服务任务及队列的内存配置需另行考虑。

## 3. CRITICAL 是什么意思？

- 表示临界区：保护共享数据操作，避免并发干扰。
- 常见宏：`taskENTER_CRITICAL()` / `taskEXIT_CRITICAL()`，必须成对，允许按移植规则嵌套。
- 常见单核 Cortex-M 移植通过屏蔽一定范围的中断保护操作，不保证屏蔽所有中断。
- 临界区尽量短，不执行延时或可能阻塞的操作；ISR 使用对应的中断版接口。
- 单独的 `CRITICAL()` 可能是项目封装，需查看定义。

## 4. 堆与任务栈的监测、异常钩子有哪些？

| 功能 | 接口 | 关键含义 |
|---|---|---|
| 当前剩余堆 | `xPortGetFreeHeapSize()` | 剩余字节，不代表最大连续空闲块 |
| 历史最小剩余堆 | `xPortGetMinimumEverFreeHeapSize()` | 运行以来堆最紧张时的余量；支持情况取决于堆实现 |
| 任务历史最小剩余栈 | `uxTaskGetStackHighWaterMark(handle)` | 传 NULL 查询当前任务；标准内核单位为 StackType_t 元素数 |
| 分配失败钩子 | `vApplicationMallocFailedHook(void)` | pvPortMalloc 分配失败时调用，不检测堆写越界 |
| 栈溢出钩子 | `vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)` | 检测到任务栈溢出时调用，不能保证捕获所有溢出 |

配置：

```c
#define INCLUDE_uxTaskGetStackHighWaterMark 1
#define configUSE_MALLOC_FAILED_HOOK       1
#define configCHECK_FOR_STACK_OVERFLOW    2
```

- 堆是动态分配池，任务栈用于局部变量、调用信息和上下文。
- 动态任务的栈可从堆分配，但栈用满与堆分配失败是不同问题。
- STM32 常见 StackType_t 为 4 字节；不同厂商移植可能调整 API 单位，应核对实现。
- 高水位是观测值，不是绝对安全保证，应覆盖最坏执行路径并保留余量。

## 5. 堆、栈监测 API 和异常钩子一般用在哪里？

- 主要用于调试、内存配置和故障定位，通常放在诊断任务、调试命令或错误处理模块。
- `xPortGetFreeHeapSize()`：检查当前剩余堆，常在初始化后或动态申请/释放时查看。
- `xPortGetMinimumEverFreeHeapSize()`：压力测试后检查历史最小余量，评估堆配置。
- `uxTaskGetStackHighWaterMark()`：任务跑过复杂路径后检查栈余量，调整创建任务时的栈大小。
- `vApplicationMallocFailedHook()` / `vApplicationStackOverflowHook()`：用户实现并开启配置，由系统在分配失败/检测到栈溢出时调用；调试时可打断点。
- 不是每轮业务处理都要调用；了解用途，排查内存问题时会查会用即可。

## 6. 多任务运行时如何获取任务最小剩余栈？是当前值吗？

- 正常多任务运行中调用 `uxTaskGetStackHighWaterMark(taskHandle)`；传 NULL 查询当前任务。
- 每个任务有自己的栈，其他任务不会正常使用它的栈；任务切换不清空栈的历史痕迹。
- 返回历史最小剩余量，不是调用瞬间的剩余量。例如曾剩 100、后来剩 800，查询仍为 100。
- 原理：创建时填充栈，查询时扫描未被改写的填充值，估算历史使用深度。
- 标准内核单位是 StackType_t 元素数；字节数＝返回值×sizeof(StackType_t)。
- 要在正常多任务环境覆盖复杂和异常路径，再看余量；未实际写入的栈空间可能使估算偏乐观，需保留余量。

## 7. 获取的最小剩余栈值会一直变化吗？

- 每次调用接口获取当时的历史最小余量；同一任务生命周期内通常只会变小或不变，不会随函数返回而回升。
- 返回值赋给普通变量后，变量不会自动刷新，需再次调用并赋值。
- 例：查询得到 100；任务以后栈使用更深，再查询可能为 60；未出现更深使用则仍为 100。

## 8. 常见内核对象的底层组成和 RAM 占用

实际大小随版本、架构、配置变化；以下是对象内存，不含堆分配头和对齐开销。

| 对象 | 底层组成 | 内存估算 |
|---|---|---|
| 任务 | TCB 控制块＋独立栈 | sizeof(StaticTask_t)＋栈深度×sizeof(StackType_t) |
| 队列 | Queue_t 控制块＋数据缓冲区 | sizeof(StaticQueue_t)＋长度×单项字节数 |
| 二值信号量 | 长度 1、单项大小 0 的队列机制 | sizeof(StaticSemaphore_t) |
| 计数信号量 | 单项大小 0 的队列机制，队列计数表示资源数量 | sizeof(StaticSemaphore_t)，不随最大计数线性增加 |
| 互斥锁/递归互斥锁 | 队列机制＋持有者、递归计数等控制信息 | sizeof(StaticSemaphore_t)，无需数据区 |
| 事件组 | 事件位＋等待任务链表 | sizeof(StaticEventGroup_t) |
| 软件定时器 | 周期、回调、ID、链表项等控制信息 | sizeof(StaticTimer_t)；另外共用服务任务和命令队列 |
| 任务通知 | TCB 内的通知值和状态 | 无独立对象分配；每槽字段为 4 字节值＋1 字节状态，结构对齐另计 |
| 流/消息缓冲区 | 控制块＋环形缓冲区 | 控制块＋缓冲区（含实现所需预留）；消息缓冲区每条消息还存长度头 |

- 队列、信号量、互斥锁复用队列机制；其余对象有自己的结构。
- 单核常规配置下控制块常为几十至百余字节量级，任务栈/数据缓冲区通常更占内存；不要背固定字节数。
- 标准 FreeRTOS 的任务栈深度单位是 StackType_t 元素数，常见 STM32 为 4 字节；厂商移植可能不同。
- 本工程可用 sizeof 对应 Static 类型查看控制块大小；动态创建前后比较 xPortGetFreeHeapSize() 可观察实际堆消耗，需排除其他分配干扰和首次共享设施初始化。
