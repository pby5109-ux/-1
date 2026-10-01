# Cortex-M3内核参考入口

先看“00-先看学习顺序.md”第三阶段；旧ARM7/9不作为你的主线。

[下载或在线打开ST PM0056 Rev7（156页）](https://www.st.com/resource/en/programming_manual/pm0056-stm32f10xxx20xxx21xxxl1xxxx-cortexm3-programming-manual-stmicroelectronics.pdf)

本轮已在线核对该文档；本机下载因TLS/连接超时失败，所以这里是**官方入口，不是离线PDF**。下载成功后可保存到本目录，不要把根目录RM0008当作M3内核手册。

选读：2.1 p13～23；2.2 p24～31；2.3 p32～38；2.4 p39～41；第4章NVIC/SCB/SysTick。按问题读，不需要通读指令集。

[Arm官方Cortex-M3核心导览](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/a-tour-of-the-cortex-m3-core)用于帮助区分模式、栈与异常，不替代具体器件手册。

[Cortex系列术语对照](仅作术语对照/Cortex系列.pdf)：p1～2架构表存在错误，勿背ARM7=ARMv6、ARM9=ARMv6等泛化；ARM7是处理器系列名，不等于ARMv7。这里只保留它帮助识别MSP/PSP、xPSR等术语。
