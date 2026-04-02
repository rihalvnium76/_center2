#include <cctype>

static inline void clrbuf(){ // clear stdin
    scanf("%*[^'\n']%*c");
}

static void trim(char *s){
    // Remove the first and last blank characters. The parameter cannot be a character constant
    if(!s) return;
    // Identify non blank parts
    int len = 0, nsp = -1, nep; // length, the start and end positions of non blank characters
    bool nspLock = false;
    char c;
    while((c=s[len])!='\0'){
        ++len;
        if(!nspLock) {
            ++nsp;
            if(!isspace(c)) nspLock = true; 
        }
    }
    if(nsp == len-1) {s[0] = '\0'; return;}
    nep = len;
    while(isspace(s[--nep])) ;
    // Move the characters
    if(nsp != -1) {
        int p = 0;
        while(nsp<=nep) {
            s[p] = s[nsp];
            ++p; ++nsp;
        }
        s[p] = '\0';
    } else s[nep] = '\0';
}
