#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#define C2i(c_ptr) *((int32_t*)c_ptr)
int32_t c2i(const char *c){
	return *((int32_t*)c);
}
int main()
{
	char a[8]={1,2,3,4,5,6,7,8};
	//(int32_t)a[0]=0xFFFF0000;  /*ERROR*/
	//(int32_t)a[4]=0x0000EEEE;
	printf("%x %x\n",sizeof(a),UCHAR_MAX);
	for(int i=0;i<8;++i)printf("%x ",a[i]);
	puts("");
	//Access method 1
	int32_t b,c;
	memcpy(&b,&a[0],4);
	memcpy(&c,&a[4],4);
	printf("%x %x\n",b,c);

	printf("%x %x\n",c2i(&a[0]),c2i(&a[4]));
	//Access mehtod 2
	printf("%x %x\n",C2i(&a[0]),C2i(&a[4])); 
	
	//Write method
	C2i(&a[0])=0x99887766;
	printf("%x\n",C2i(&a[0]));
	
	//Simulate union
	int32_t d=0x11223344;
	for(int i=0;i<4;++i)printf("%x ",((char*)&d)[i]);
	return 0;
}
