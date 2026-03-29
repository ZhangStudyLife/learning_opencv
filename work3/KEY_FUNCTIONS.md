# work3 关键脚本与通信函数说明

## 1. 这份文档是干什么的

这个文档专门回答两个问题：

1. `work3` 里面哪个脚本最重要
2. 哪些函数是真正负责“通信”和“数据传递”的关键函数

如果你想快速理解整个项目，最应该先看这份文档，再去看源码。

---

## 2. 整个项目最重要的脚本

从“项目主链是否跑得通”的角度看，最重要的是下面 4 个脚本：

### 2.1 `src/ball_detector.py`

这是整个项目的输入源入口，也是最关键的上游节点。

作用：

- `video` 模式下读取 MP4/摄像头
- `mouse` 模式下读取鼠标位置
- 把输入统一转换成 ROS 话题

它是整个系统的“数据源头”。

如果这个脚本不工作，后面的控制器、Gazebo、监视窗口都会断掉。

### 2.2 `src/mecanum_controller.py`

这是控制核心。

作用：

- 订阅红球位置
- 计算 `/cmd_vel`
- 让小车真正得到运动命令

它是整个系统的“控制决策中心”。

### 2.3 `src/mecanum_visualizer.py`

这是调试和展示核心。

作用：

- 订阅图像和控制结果
- 展示左侧输入源图像
- 展示右侧方向箭头和底盘状态

它不是控制必须环节，但它是你理解系统是否正常工作的最重要可视化窗口。

### 2.4 `launch/mecanum_sim.launch`

这是完整系统的总入口。

作用：

- 启动 Gazebo
- 启动模型
- 启动输入节点
- 启动控制器
- 启动监视窗口

如果把整个项目看成一个程序，这个 launch 文件就是“总开关”。

---

## 3. 最重要的通信链路

整个项目最核心的通信链路是：

```text
ball_detector.py
    -> /ball_position
    -> /ball_detected
    -> /camera/image_processed

mecanum_controller.py
    <- /ball_position
    <- /ball_detected
    -> /cmd_vel

mecanum_visualizer.py
    <- /camera/image_processed
    <- /ball_position
    <- /ball_detected
    <- /cmd_vel

Gazebo planar_move 插件
    <- /cmd_vel
    -> /odom
```

简单说就是：

1. `ball_detector.py` 负责“发消息”
2. `mecanum_controller.py` 负责“收消息再转成控制命令”
3. `mecanum_visualizer.py` 负责“收消息做展示”
4. Gazebo 插件负责“收 `/cmd_vel` 让小车动起来”

---

## 4. 最重要的通信函数

下面这些函数，是整个项目中最值得优先理解的函数。

---

### 4.1 `ball_detector.py` 中最重要的函数

#### `run()`

这是输入节点的主循环函数。

作用：

- 根据 `input_mode` 选择执行 `handle_video_mode()` 或 `handle_mouse_mode()`
- 持续把输入源转成 ROS 消息

为什么重要：

- 它决定整个项目的数据从哪里来
- 它是输入链路的总调度函数

#### `handle_video_mode()`

这是视频模式的核心函数。

作用：

- 读取视频帧
- 检测红球
- 计算归一化坐标
- 发布 ROS 消息

为什么重要：

- 这是 MP4 红球控制链的核心入口

#### `handle_mouse_mode()`

这是鼠标模式的核心函数。

作用：

- 生成操控台画面
- 获取鼠标位置
- 直接把鼠标位置当成红球位置
- 发布 ROS 消息

为什么重要：

- 这是虚拟摇杆控制链的核心入口

#### `publish_ball_state(norm_x, norm_y, radius, detected, vis_frame)`

这是 `ball_detector.py` 里最关键的“通信函数”。

作用：

- 发布 `/ball_detected`
- 发布 `/ball_position`
- 发布 `/camera/image_processed`

为什么最关键：

- 这是输入节点真正把数据送出去的地方
- 它是整个项目最核心的 ROS 发布函数之一

可以把它理解成：

```text
输入源 -> ROS 通信出口
```

#### `detect_ball_from_video(frame)`

这是视频模式下的识别核心函数。

作用：

- 提取红色区域
- 找出最佳红球轮廓
- 生成可视化图像

为什么重要：

- 它决定能不能从视频里正确找到红球

---

### 4.2 `mecanum_controller.py` 中最重要的函数

#### `compute_target_command()`

这是控制器最重要的决策函数。

作用：

- 读取最新的 `norm_x / norm_y`
- 调用映射逻辑计算目标速度

为什么重要：

- 它决定红球位置最后会变成什么样的车速

#### `publish_cmd(cmd)`

这是控制器里最关键的“通信函数”。

作用：

- 把计算后的速度封装为 `Twist`
- 发布到 `/cmd_vel`

为什么最关键：

- 这是整个控制链真正把命令送给 Gazebo 的出口
- 没有它，小车就不会动

可以把它理解成：

```text
控制结果 -> ROS 控制命令出口
```

#### `run()`

这是控制器主循环。

作用：

- 持续调用 `compute_target_command()`
- 做平滑处理
- 调用 `publish_cmd()`

为什么重要：

- 它把订阅、计算、发布整合成一个完整控制闭环

#### `ball_position_callback(msg)`

这是控制器的重要订阅回调函数。

作用：

- 接收 `/ball_position`
- 保存最新红球位置

为什么重要：

- 这是控制器接收上游输入消息的关键入口

#### `ball_detected_callback(msg)`

作用：

- 接收 `/ball_detected`
- 更新目标是否可用

为什么重要：

- 它决定丢球保护逻辑是否触发

---

### 4.3 `mecanum_visualizer.py` 中最重要的函数

#### `compose_window()`

这是监视窗口最核心的拼装函数。

作用：

- 组合左侧输入画面
- 组合右侧底盘箭头图
- 最终生成 `work3 monitor`

为什么重要：

- 它决定你最终看到的整个监控画面是什么样子

#### `image_callback(msg)`

作用：

- 订阅 `/camera/image_processed`
- 保存输入源图像

为什么重要：

- 这是监视窗口接收上游图像的关键入口

#### `cmd_vel_callback(msg)`

作用：

- 订阅 `/cmd_vel`
- 保存当前控制命令

为什么重要：

- 它让右侧箭头和小车目标方向保持同步

#### `overlay_status(frame)`

作用：

- 在画面顶部写入 `source`、检测状态、坐标、速度

为什么重要：

- 这是你调试时最直接的信息显示函数

---

### 4.4 `mecanum_logic.py` 中最重要的函数

#### `ball_position_to_cmd(norm_x, norm_y, max_linear_speed, deadzone_x, deadzone_y)`

这是整个项目最重要的纯逻辑函数。

作用：

- 把红球位置映射成小车线速度

为什么重要：

- 它决定“红球往哪，小车往哪”
- 项目控制语义的核心就在这里

#### `pixel_position_to_normalized(pixel_x, pixel_y, frame_width, frame_height)`

作用：

- 把像素位置换成 `[-1, 1]` 范围的标准化坐标

为什么重要：

- `video` 模式和 `mouse` 模式都要靠它统一坐标语义

#### `apply_deadzone(value, deadzone)`

作用：

- 给中心区域加死区

为什么重要：

- 决定小车能不能稳定停住

---

## 5. 哪一个函数最像“通信总枢纽”

如果只选一个“最像通信枢纽”的函数，我给你两个答案：

### 上游通信总枢纽

`ball_detector.py` 里的：

```python
publish_ball_state(...)
```

原因：

- 它把输入源变成 ROS 话题
- 它一次性发布 3 个关键消息
- 它是整个系统的数据出口

### 下游通信总枢纽

`mecanum_controller.py` 里的：

```python
publish_cmd(...)
```

原因：

- 它把控制器计算结果变成 `/cmd_vel`
- 它是小车真正收到命令的最后一步

所以最准确的说法是：

```text
publish_ball_state() 是输入通信枢纽
publish_cmd() 是控制通信枢纽
```

---

## 6. 如果只看源码，推荐阅读顺序

建议按这个顺序看：

1. `launch/mecanum_sim.launch`
2. `src/ball_detector.py`
3. `src/mecanum_controller.py`
4. `src/mecanum_logic.py`
5. `src/mecanum_visualizer.py`

原因：

- 先看总入口
- 再看输入怎么来
- 再看控制怎么算
- 再看底层数学逻辑
- 最后看监视和调试界面

---

## 7. 一句话总结

如果你要用最短的话概括整个项目：

```text
ball_detector.py 负责把输入源转换成 ROS 消息，
mecanum_controller.py 负责把 ROS 消息转换成 /cmd_vel，
publish_ball_state() 和 publish_cmd() 是整个项目最关键的两个通信函数。
```
