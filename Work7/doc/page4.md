:::color2
`<font style="color:rgb(6, 6, 7);">` GMapping 基于激光雷达数据实现机器人同步定位与建图，通过粒子滤波融合激光扫描与里程计信息，构建二维栅格地图，是 ROS 移动机器人导航的经典SLAM算法。  `</font>`

:::

#### SLAM 算法流程（ 以GMapping为例）

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`以基于激光雷达的 SLAM 算法 GMapping 为例，机器人的 SLAM 过程可以概括为：`</font><font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">`在未知环境中移动的同时，`</font>`**`<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">`同步完成自身定位与环境地图构建`</font>`**`<font style="color:#DF2A3F;background-color:rgba(0, 0, 0, 0);">`。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`GMapping 是一种经典的开源 2D 激光 SLAM 算法，核心基于 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`粒子滤波 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`技术实现机器人位姿估计与地图更新。算法通过激光雷达获取环境距离信息，结合机器人里程计运动数据，不断估计自身在环境中的位置；同时根据当前定位结果，逐步构建并更新`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`栅格地图`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，实现“一边定位、一边建图”。在整个过程中，机器人通过持续运动与观测，不断优化自身位置与地图精度，最终得到一张可用作导航的环境栅格地图，因此在移动机器人自主导航中应用十分广泛。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2026/png/54556538/1775927396942-feded1e9-442a-43ff-8dd7-0ebbb9c8691b.png" width="596.2000122070312" title="" crop="0,0,1,1" id="ue8f0bd04" class="ne-image">

#### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`GMapping 建图的步骤：`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`GMapping 的 SLAM 过程是一个迭代优化的过程，具体步骤如下：`</font>`

1. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`初始化粒子群`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：生成一组随机粒子，每个粒子代表机器人的一种可能初始位姿。`</font>`
2. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`位姿预测`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：根据运动模型（结合里程计），预测每个粒子的下一个位姿，并加入运动噪声。`</font>`
3. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`权重计算`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：基于激光雷达传感器数据，计算每个粒子的权重，评估该粒子位姿与实际观测的匹配程度。`</font>`
4. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`粒子重采样`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：根据权重重采样，保留高权重粒子、丢弃低权重粒子，生成新的粒子群，提升位姿估计精度。`</font>`
5. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`地图更新`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：每个粒子根据自身对应的位姿，结合激光观测数据，更新地图中对应栅格的占据概率。`</font>`
6. **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`迭代循环`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：重复步骤 2-5，随着机器人持续移动、不断采集传感器数据，粒子群会逐渐收敛到机器人的真实位姿，地图精度也不断提升，直至完成整个环境的地图构建。`</font>`

:::color2
`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`注：地图构建为`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`渐进式过程`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，机器人移动范围越广、采集的数据越充分，地图的完整性和精度越高；粒子群的收敛过程，也是机器人位姿估计从不确定到精准的过程。`</font>`

:::

<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1744096691370-0f52c74d-70d5-4970-b339-596f9df5f3a5.png" width="754" title="" crop="0,0,1,1" id="Rg4aw" class="ne-image">

    上图是机器人`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在gazebo`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`仿真环境`</font>`**中的运动过程；下图是在RViz中观察到的GMapping 算法**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`实时构建的栅格地图`</font>`**。

地图上，灰色 = 已探索区域，黑色 = 障碍物，红色 = 激光扫描范围，黑点 = 机器人估计位姿。

##### `<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`粒子滤波（估计位姿）`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`GMapping 通过粒子滤波实现机器人的位姿估计，通过一组粒子模拟机器人的可能位姿，逐步收敛到真实位姿，具体步骤如下：`</font>`

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`粒子表示`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：每个粒子对应机器人的一种可能位姿（包含位置和方向），粒子群整体反映机器人位姿的不确定性。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`初始化`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：算法启动时，生成一组随机分布的粒子，覆盖机器人可能的位姿范围。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`预测`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：根据机器人的运动模型，结合里程计数据，预测每个粒子的下一个位姿，并加入适量运动噪声，模拟实际运动中的不确定性，如地面打滑、电机误差。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`更新`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：利用激光雷达采集的环境数据，计算每个粒子的权重： 权重越高，代表该粒子对应的位姿，与激光观测数据的匹配度越高，即该位姿越接近机器人真实位姿。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`重采样`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：按照粒子权重重新采样，保留高权重粒子（大概率接近真实位姿），丢弃低权重粒子，以减少计算量并提高估计精度。`</font>`

##### 概率栅格地图（建图）

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`GMapping 构建的是概率栅格地图，通过栅格概率描述环境中区域的占用状态，为后续导航提供精准环境基准：`</font>`

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`地图表示`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：将环境划分为均匀大小的栅格，每个栅格用“占据概率” 描述该区域是否存在障碍物：占据概率越高，代表该区域有障碍物的可能性越大；初始状态下，所有栅格的占据概率设为均匀分布。`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`更新机制`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：随着机器人移动，结合激光雷达观测数据和粒子对应的位姿，逐一对栅格的占据概率进行更新：若激光检测到某栅格存在障碍物，则该栅格的占据概率增加、空闲概率减少；反之则降低占据概率，逐步明确环境布局。`</font>`

#### GMapping 功能包：话题、服务与参数

GMapping 通过订阅传感器数据、发布地图信息，并提供相关服务与可调参数，实现机器人在未知环境中的同步定位与地图构建。

1. **话题 (Topics)**:
   - **`<font style="color:#DF2A3F;">`订阅的话题`</font>`**
     * `/scan` (类型: `**<font style="color:#DF2A3F;">sensor_msgs/LaserScan</font>**`): 接收来自激光雷达的扫描数据，用于构建环境地图。
     * `/odom` (类型: `nav_msgs/Odometry`): 接收机器人的位姿信息，辅助定位和地图更新。
     * `/tf` (类型: `<font style="color:#DF2A3F;">tf/tfMessage</font>`): 订阅激光雷达坐标系、基坐标系、里程计坐标系之间的变换。
   - **`<font style="color:#DF2A3F;">`发布的话题`</font>`**`<font style="color:#DF2A3F;">`:`</font>`
     * `/map` (类型: `nav_msgs/OccupancyGrid`): 发布构建得到的二维环境地图，表示区域的占用情况。
2. **服务 (Services)**:
   - `/gmapping/initialpose` (类型: `geometry_msgs/PoseWithCovarianceStamped`): 设置初始位置，帮助定位初始化。
   - `<font style="color:#DF2A3F;">/gmapping/save_map</font>` (类型: 通常自定义服务): 提供保存当前地图到文件的功能，方便后续使用和分析。
3. **参数 (Parameters)**:
   - `linearUpdate`: 控制地图更新的频率，当机器人移动超过该距离时触发更新。
   - `angularUpdate`: 当机器人旋转超过指定角度时触发地图更新。
   - `maxUdatingAge`: 确定用于更新地图的数据的时间限制，避免使用过时的信息。
4. **配置文件**:
   - 通常是 `gmapping.yaml`，包含参数的默认值和用户自定义设置，便于管理和调整GMapping的行为。
     通过合理配置这些主题、服务和参数，可以优化GMapping在不同环境中的性能，确保高效的地图构建和定位。

#### TF工具

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`由于里程计存在累积误差，坐标系间的关系会随机器人运动动态变化，若缺乏统一的坐标管理，多源数据将无法正确融合。TF 系统通过维护完整的坐标变换树，确保所有节点能够实时获取准确的坐标转换关系，从根本上保障了机器人定位、建图与导航的系统一致性和数据准确性。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`在移动机器人导航系统中，有 `</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`map、odom、base_link`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 是三个坐标系，共同构成了机器人定位与导航的空间基准：`</font>`

+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`base_link`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：机器人本体坐标系，固定于机器人底盘中心，随机器人运动而实时变化，是所有传感器、执行器的局部参考基准；`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`odom`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：里程计坐标系，以机器人初始位置为原点，通过轮式里程计等传感器推算机器人的局部运动位姿，会因传感器误差产生累积漂移，仅适用于短时间、局部范围的位姿估计；`</font>`
+ **`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`map`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`：全局静态坐标系，以环境地图为基准，是机器人在整个工作空间中的绝对参考系，用于全局路径规划与定位。`</font>`

`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`GMapping 算法通过激光雷达扫描匹配，实时估计机器人在全局地图中的位姿，并`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`发布 `</font>`**`**<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">map → odom</font>**`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 的坐标变换`</font>`**`<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">`，将里程计的局部位姿校正到全局坐标系下，从而实现激光雷达、里程计等多源数据在 `</font><font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">map</font>``<font style="color:rgb(0, 0, 0);background-color:rgba(0, 0, 0, 0);">` 坐标系下的统一融合与处理。`</font>`

<img src="https://cdn.nlark.com/yuque/0/2025/png/54556538/1742131171663-c2331ca4-3538-499f-82d2-cd92c9f05c93.png" width="705.4000244140625" title="" crop="0,0,1,1" id="u9aa75228" class="ne-image">

`<font style="color:rgb(41, 36, 33);">`坐标变换包括了位置和姿态的变化，ROS中的 tf2 以树形结构记录多个坐标系之间的关系，并允许用户在任何期望的时间点在任意两个坐标系之间进行转换。`</font>`

`<font style="color:rgb(41, 36, 33);">`参考：`</font>`

[D5.2 认识 tf2](https://www.yuque.com/shellcore/hob75t/bh0lso5mcbaw7duo)

### 总结

GMapping 使用激光雷达（LIDAR）数据来构建环境地图。激光雷达通过扫描周围环境并测量物体的距离，生成点云数据。GMapping处理这些点云数据，结合机器人的位置信息，逐步构建出环境的二维栅格地图，尽管在动态环境中有局限，但其在静态环境中的表现优异。
