# Coverage
iOS增量代码覆盖率工具


## config 

下载到本地通过pod导入到工程中

xcode->build phases->new run script phase 添加exportenv.sh脚本 例如: ../../Coverage/exportenv.sh

建议新添加一个基于DEBUG的scheme
xcode->build setttings:GCC_GENERATE_TEST_COVERAGE_FILES GCC_INSTRUMENT_PROGRAM_FLOW_ARCS设置为YES
(新添加scheme需要设置 GCC_OPTIMIZATION_LEVEL  GCC_PREPROCESSOR_DEFINITIONS)

修改main函数
CODECOVERAGE在GCC_PREPROCESSOR_DEFINITIONS里面定义
#if CODECOVERAGE
#import <RCodeCoverage/GCDAProfiling.h>
#endif
int main(int argc, char * argv[]) {
    @autoreleasepool {
#if CODECOVERAGE
        CODE_CCOVER_START
#endif
        return UIApplicationMain(argc, argv, nil, NSStringFromClass([AppDelegate class]));
    }
}

git commit之后 执行 python coverage.py (你的工程目录) 会添加覆盖率信息到commit-msg 这一步可以自定义push脚本  


