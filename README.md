湖北汽车工业学院某某校园自动信息收集 
====  
#**适用于**：
---
湖北汽车工业学院<br>
湖北汽车工业学院科技学院<br><br>


#注意事项：
---
* 教务处默认密码是身份证后四位，**默认密码无法进行自动打卡**(获取不到MOD_AUTH_CAS)，使用前先登录自己的教务处网站更改密码
* 出现问题联系QQ**878375551**，其他学校适配请提供账号密码

#配置
-----
* 将config文件重命名为**config.ini**，然后在里面填写相关配置信息
* ~~Serve酱推送Key（选填）<br><br>~~

#Linux服务器使用教程
---
* 安装好python环境
* 上传代码到某个文件夹下
* 填写配置信息
* **在代码的文件夹下打开终端**，输入 pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
* 设置crontab定时任务，29 7,8 * * * 这里是python的路径 这里是python文件的路径 >> 这里是日志的路径/1.log 2>&1
* 例如：29 7,8 * * * /root/.pyenv/shims/python /root/Python/index.py >> /root/Python/1.log 2>&1




