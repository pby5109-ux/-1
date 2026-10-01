#include <stdint.h>
#include <stddef.h>
#include <limits.h>
_Static_assert(CHAR_BIT==8, "8-bit byte");
_Static_assert(sizeof(short)==2, "short 2");
_Static_assert(sizeof(int)==4, "int 4");
_Static_assert(sizeof(long)==4, "long 4");
_Static_assert(sizeof(long long)==8, "long long 8");
_Static_assert(sizeof(void*)==4, "pointer 4");
_Static_assert(sizeof(int(*)(int))==4, "this ARM ABI function pointer 4");
_Static_assert(sizeof(uint16_t[1024])==2048, "ADC bytes");
_Static_assert(sizeof(int*[4])==16, "pointer array");
_Static_assert(sizeof(int(*)[4])==4, "array pointer");
struct Sample { char flag; int value; short channel; };
_Static_assert(sizeof(struct Sample)==12, "default struct size");
_Static_assert(offsetof(struct Sample,value)==4, "value offset");
_Static_assert(offsetof(struct Sample,channel)==8, "channel offset");
_Static_assert(_Alignof(struct Sample)==4, "struct alignment");
#pragma pack(push,1)
struct Packed { int i; double d; char c; };
#pragma pack(pop)
_Static_assert(sizeof(struct Packed)==13, "specific compiler pack behavior");
#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "Exercise model assumes little endian"
#endif
int model_verified(void) { return 1; }
