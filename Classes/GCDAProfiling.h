

#define CODE_CCOVER_START NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);\
NSString *documentsDirectory = [[paths objectAtIndex:0] stringByAppendingPathComponent:@"gcda_files"];\
setenv("GCOV_PREFIX", [documentsDirectory cStringUsingEncoding:NSUTF8StringEncoding], 1);\
setenv("GCOV_PREFIX_STRIP", "14", 1);\
dispatch_source_t timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, dispatch_get_global_queue(0, 0));\
dispatch_source_set_timer(timer, DISPATCH_TIME_NOW, 2 * NSEC_PER_SEC, 0 * NSEC_PER_SEC);\
dispatch_source_set_event_handler(timer, ^{\
    __gcov_flush_r();\
});\
dispatch_resume(timer);\


void __gcov_flush_r();
