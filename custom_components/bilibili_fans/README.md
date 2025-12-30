# Bilibili Fans Monitor

Home Assistant集成，用于监控哔哩哔哩账号的粉丝数量及相关数据。

## 功能特点

- 🔍 **实时粉丝数量**：显示当前账号的粉丝数量
- 📊 **关注数量**：显示账号的关注数量
- 📈 **本月新增粉丝**：从每月1日开始统计的新增粉丝数量
- 📉 **本年新增粉丝**：从每年1日开始统计的新增粉丝数量
- 🎯 **支持多账号**：可以同时监控多个B站账号
- 🎨 **自定义名称**：支持为每个传感器设置自定义名称
- ⚡ **自动更新**：每小时自动更新一次数据
- 🖥️ **UI配置**：支持通过Home Assistant界面轻松配置
- 📝 **YAML配置**：支持传统的YAML配置方式

## 安装方法

### 方法一：手动安装

1. 下载本仓库的所有文件
2. 将文件复制到Home Assistant的 `config/custom_components/bilibili_fans/` 目录下
3. 重启Home Assistant服务

### 方法二：通过HACS安装

（暂未发布到HACS，敬请期待）

## 配置方法

### 方法一：UI配置

1. 进入Home Assistant界面
2. 点击左侧菜单的「配置」
3. 选择「设备与服务」
4. 点击右上角的「添加集成」
5. 在搜索框中输入「Bilibili Fans」并选择
6. 在配置页面中：
   - 输入B站ID
   - （可选）输入自定义名称
7. 点击「提交」
8. 集成添加成功后，传感器将显示在传感器列表中

### 方法二：YAML配置

在 `configuration.yaml` 文件中添加以下配置：

```yaml
sensor:
  - platform: bilibili_fans
    vmid: 您的B站ID
    name: 自定义名称  # 可选
```

保存文件后，重启Home Assistant服务或执行「配置检查」和「重载配置」

## 传感器说明

### 状态值

- **粉丝数量**：当前账号的粉丝数量

### 属性

| 属性名 | 描述 |
|--------|------|
| following | 账号的关注数量 |
| mid | B站账号ID |
| monthly_increase | 本月新增粉丝数量（每月1日重置） |
| yearly_increase | 本年新增粉丝数量（每年1日重置） |
| month_start_follower | 本月初的粉丝数量 |
| year_start_follower | 本年初的粉丝数量 |

## 数据更新

- 传感器每小时自动更新一次数据
- 您也可以在传感器详情页手动点击「刷新」按钮获取最新数据
- 每月1日自动重置本月新增粉丝统计
- 每年1日自动重置本年新增粉丝统计

## 注意事项

- 本集成使用B站公开API，无需登录或认证
- API请求频率为每小时一次，符合B站API的使用规范
- 如果传感器显示为unavailable，请检查网络连接或B站API是否正常

## 更新日志

### v1.0.0 (2025-12-30)

- 首次发布
- 支持实时粉丝数量监控
- 支持本月和本年新增粉丝统计
- 支持UI和YAML配置
- 支持自定义传感器名称

## 许可证

MIT License

## 反馈与贡献

如果您在使用过程中遇到问题或有改进建议，欢迎在GitHub仓库提交Issue或Pull Request。

GitHub仓库：[https://github.com/chaosl1996/bilibi_fans](https://github.com/chaosl1996/bilibi_fans)

## 致谢

- 感谢B站提供公开的API接口
- 感谢Home Assistant社区的支持和帮助
