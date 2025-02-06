## 出包指南
=====================================
#### 全局env值
1. 检查gitlab本项目页面下的Settings->CI/CD->Variables
#### 出包配置文件
1. client/build_env.ini
2. 文件中有注释

#### 出Android包
1. CI/CD
2. Run pipeline
3. Variables 设置，可以为空，为空时直接出release包
   1. key: BuildOptions
   2. value: UnityEditor.BuildOptions 的enum名，确保大小写一致。多个值以','分割
      1. 常用值:Development AllowDebugging EnableDeepProfilingSupport
      2. flag enum
4. 点击Run pipeline按钮
5. 点击build-android-app右边的play按钮
6. build完成后自动拷贝到 *\\192.168.10.250\cwcx\ch_new\apk* 下

#### 出asset bundles补丁
1. CI/CD
2. Run pipline
3. 不设置任何Variables
4. 点击Run pipline按钮
5. 点击build-xxxx-bundles
6. 可以先后运行两个build-ios-bundles/build-android-bundles 会顺序执行
7. build完成后自动拷贝到 *\\192.168.10.250\cwcx\ch_new\cdn* 下