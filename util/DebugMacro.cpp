#include <cstdio>

#define DEBUG_

// Debug Output Macro
/*
  DBG_C_PTR : Debug output Control Pointer (bool* type)
  dbgt : Set TAG
  dbgc : Set DBG_C_PTR
  dbgo : Debug output code with the control of debug output switch
  dbgv/dbgi/dbgd/dbgw/dbge :
    Encapsulation of dbgo marco, ouput with different log level   
*/
#ifdef DEBUG_

static bool *DBG_C_PTR = NULL;

#define dbgt(T) const char *TAG = #T;
#define dbgc(C_PTR) DBG_C_PTR = (C_PTR);

#define dbgo(M, FMT, ...) if(!DBG_C_PTR || *DBG_C_PTR) fprintf(stderr, "[" #M "]%s#%d: " FMT, TAG, __LINE__, ##__VA_ARGS__);
#define dbgv(FMT, ...) dbgo(V, FMT, ##__VA_ARGS__)
#define dbgi(FMT, ...) dbgo(I, FMT, ##__VA_ARGS__)
#define dbgd(FMT, ...) dbgo(D, FMT, ##__VA_ARGS__)
#define dbgw(FMT, ...) dbgo(W, FMT, ##__VA_ARGS__)
#define dbge(FMT, ...) dbgo(E, FMT, ##__VA_ARGS__)

#else
#define dbgt(T)
#define dbgc(C_PTR)
#define dbgo(M, FMT, ...)
#define dbgv(FMT, ...)
#define dbgi(FMT, ...)
#define dbgd(FMT, ...)
#define dbgw(FMT, ...)
#define dbge(FMT, ...)
#endif

int main() {
    dbgt(main)

    bool dbg;
    dbgc(&dbg) // bind switch variable

    dbg = true;
    dbgv("Test1")
    dbg = false;
    dbgv("Test2")
    puts("--END");
    return 0;
}
