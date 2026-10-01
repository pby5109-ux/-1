#include <stdio.h>
#include <stdlib.h>
#include "参考实现.c"

static unsigned long checks;
#define CHECK(x) do { ++checks; if (!(x)) { \
    fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); return 1; \
} } while (0)

static size_t ref_digit_len(const char *s, size_t *pos) {
    size_t best = 0;
    *pos = SIZE_MAX;
    for (size_t i = 0; s[i] != '\0'; ++i) {
        size_t k = i;
        while (s[k] >= '0' && s[k] <= '9') ++k;
        if (k - i > best) { best = k - i; *pos = i; }
    }
    return best;
}

static bool ref_palindrome(const char *s) {
    unsigned char tmp[64];
    size_t n = 0;
    for (size_t i = 0; s[i] != '\0'; ++i) {
        unsigned char c = (unsigned char)s[i];
        if (c >= 'A' && c <= 'Z') c = (unsigned char)(c - 'A' + 'a');
        if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) tmp[n++] = c;
    }
    for (size_t i = 0; i < n / 2; ++i) if (tmp[i] != tmp[n-1-i]) return false;
    return true;
}

static int next_value(void) {
    int a = 0;
    static int b;
    return ++a + ++b;
}

int main(void) {
    _Static_assert(CHAR_BIT == 8, "Tests assume octets");
    _Static_assert(sizeof(int) == 4, "Tests assume 32-bit int");
    _Static_assert(sizeof(uint32_t) == 4, "uint32_t size");
    printf("Host pointer=%zu, int=%zu, long=%zu, plain_char_signed=%d\n",
           sizeof(void *), sizeof(int), sizeof(long), CHAR_MIN < 0);

    /* C02: evaluate the defined macro examples; do not run SQUARE(i++). */
    #define SQUARE(x) x*x
    #define MIN(a,b) ((a)<(b)?(a):(b))
    int r = SQUARE(2+1);
    int i = 1;
    int m = MIN(i++, 5);
    CHECK(r == 5 && m == 2 && i == 3);
    CHECK(60UL * 60UL * 24UL * 365UL == 31536000UL);
    CHECK(next_value() == 2);
    CHECK(next_value() == 3);
    CHECK(next_value() == 4);

    char text[] = "ab\0cd";
    int unchanged = 1;
    CHECK(sizeof(text) == 6 && strlen(text) == 2);
    CHECK(sizeof(unchanged++) == 4 && unchanged == 1);
    int a[10] = {1,2,3,4,5,6,7,8,9,0};
    int *q = &a[1];
    int matrix[2][3] = {{1,2,3},{4,5,6}};
    int (*row)[3] = matrix;
    const char *str[] = {"ab","cd","ef","gh","ij"};
    CHECK(q[6] == 8 && row[1][2] == 6 && 2[a] == 3);
    CHECK(strcmp((str+4)[-1], "gh") == 0);
    CHECK(a[0] == 1 && (a+10)[-1] == 0);

    unsigned int u = 6;
    int s = -20;
    CHECK(u + s > 6U);
    CHECK(!(-1 < 1U));
    unsigned char x8 = 200, y8 = 100;
    int sum = x8 + y8;
    unsigned char narrowed = (unsigned char)(x8+y8);
    CHECK(sum == 300 && narrowed == 44 && (uint8_t)300 == 44);
    CHECK(UINT_MAX + 1U == 0U);
    CHECK((int)-3.9 == -3);
    struct Sample { char flag; int value; short channel; };
    struct Compact { int value; short channel; char flag; };
    CHECK(offsetof(struct Sample, value) == 4);
    CHECK(offsetof(struct Sample, channel) == 8);
    CHECK(sizeof(struct Sample) == 12 && sizeof(struct Compact) == 8);
    char moved[] = "ABCDE";
    memmove(moved+1,moved,4);
    CHECK(strcmp(moved,"AABCD") == 0);

    uint32_t endian = UINT32_C(0x12345678);
    CHECK(((unsigned char *)&endian)[0] == 0x78);
    uint32_t bytes[10] = {0,1,2,3,4,5,6,7,8,9};
    memcpy(bytes+3,bytes,5);
    const uint32_t expected5[10] = {0,1,2,0,1,5,6,7,8,9};
    CHECK(memcmp(bytes,expected5,sizeof bytes) == 0);
    uint32_t words[10] = {0,1,2,3,4,5,6,7,8,9};
    memmove(words+3,words,5*sizeof words[0]);
    const uint32_t expected20[10] = {0,1,2,0,1,2,3,4,8,9};
    CHECK(memcmp(words,expected20,sizeof words) == 0);
    /* Explicit byte arrays model the big-endian C33 branch. */
    unsigned char big[40] = {0};
    for (unsigned n=0; n<10; ++n) big[4*n+3]=(unsigned char)n;
    memcpy(big+12,big,5);
    CHECK(big[12]==0 && big[15]==0 && big[16]==0 && big[19]==4);

    uintptr_t v = (uintptr_t)0x20000013;
    CHECK((v & ~(uintptr_t)7) == (uintptr_t)0x20000010);
    CHECK(((v+7) & ~(uintptr_t)7) == (uintptr_t)0x20000018);
    uint32_t flags = 0;
    flags |= UINT32_C(1)<<3;
    CHECK(flags == 8);
    flags ^= UINT32_C(1)<<3;
    CHECK(flags == 0);
    flags = UINT32_MAX;
    flags &= ~(UINT32_C(1)<<3);
    CHECK((flags & 8U)==0 && ((UINT32_C(0xA5)>>4)&0xFU)==10);
    volatile uint32_t sample = UINT32_MAX;
    CHECK(square_sample(&sample) == UINT64_C(18446744065119617025));

    for (unsigned n=0; n<256; ++n) {
        unsigned ref = 0;
        for (unsigned bit=0; bit<8; ++bit) if ((n & (1U<<bit)) != 0) ref |= 1U<<(7-bit);
        CHECK(reverse8((uint8_t)n)==ref);
        CHECK(reverse8(reverse8((uint8_t)n))==n);
    }
    CHECK(reverse8(0xA6)==0x65);
    CHECK(!reverse_text(NULL));
    const char *originals[] = {"", "a", "ab", "abc", "abcd", "12345"};
    const char *reversed[] = {"", "a", "ba", "cba", "dcba", "54321"};
    for(size_t k=0;k<sizeof originals/sizeof originals[0];++k){
        char buf[32]; strcpy(buf,originals[k]);
        CHECK(reverse_text(buf)); CHECK(strcmp(buf,reversed[k])==0);
    }

    size_t pos=0,len=0;
    CHECK(!longest_digits(NULL,&pos,&len));
    CHECK(!longest_digits("abc",NULL,&len));
    CHECK(!longest_digits("abc",&pos,NULL));
    CHECK(longest_digits("a12b345c67",&pos,&len) && pos==4 && len==3);
    CHECK(longest_digits("12a34",&pos,&len) && pos==0 && len==2);
    CHECK(longest_digits("abc",&pos,&len) && pos==SIZE_MAX && len==0);

    /* Exhaust all strings up to length 6 over {a,b,1,2}. */
    for (unsigned size=0; size<=6; ++size) {
        unsigned total=1U << (2U*size);
        for (unsigned value=0;value<total;++value) {
            char buf[7]; unsigned encoded=value;
            const char alphabet[]="ab12";
            for(unsigned k=0;k<size;++k){buf[k]=alphabet[encoded&3U];encoded>>=2;}
            buf[size]='\0'; size_t expected_pos;
            size_t expected_len=ref_digit_len(buf,&expected_pos);
            CHECK(longest_digits(buf,&pos,&len));
            CHECK(pos==expected_pos && len==expected_len);
        }
    }

    for(uint32_t n=0;n<5000;++n){
        bool prime=n>=2;
        for(uint32_t d=2;d<n && prime;++d) if(n%d==0) prime=false;
        CHECK(is_prime(n)==prime);
    }
    CHECK(!is_prime(49) && is_prime(97));
    CHECK(is_prime(UINT32_C(4294967291)) && !is_prime(UINT32_MAX));
    CHECK(swap32(UINT32_C(0x12345678))==UINT32_C(0x78563412));
    CHECK(swap32(0)==0 && swap32(UINT32_MAX)==UINT32_MAX);
    uint32_t rng=123;
    for(unsigned n=0;n<10000;++n){
        rng = rng * UINT32_C(1664525) + UINT32_C(1013904223);
        uint32_t ref = 0, remain=rng;
        for(unsigned byte=0;byte<4;++byte){ref=(ref<<8)|(remain&0xFFU);remain>>=8;}
        CHECK(swap32(rng)==ref);
        CHECK(swap32(swap32(rng))==rng);
    }

    CHECK(!palindrome(NULL));
    CHECK(palindrome("") && palindrome(".,") && palindrome("A man, a plan, a canal: Panama"));
    CHECK(!palindrome("ab"));
    for(unsigned size=0;size<=5;++size){
        unsigned total=1;for(unsigned n=0;n<size;++n)total*=5;
        for(unsigned value=0;value<total;++value){
            char buf[6];unsigned encoded=value;const char alphabet[]="aA1,!";
            for(unsigned k=0;k<size;++k){buf[k]=alphabet[encoded%5];encoded/=5;}
            buf[size]='\0';CHECK(palindrome(buf)==ref_palindrome(buf));
        }
    }

    char out[5]="KEEP";
    CHECK(!copy_text(out,sizeof out,"12345") && strcmp(out,"KEEP")==0);
    CHECK(copy_text(out,sizeof out,"1234") && strcmp(out,"1234")==0);
    CHECK(copy_text(out,1,"") && out[0]=='\0');
    CHECK(!copy_text(out,0,"") && !copy_text(NULL,4,"a") && !copy_text(out,4,NULL));
    for(size_t dst=0;dst<=10;++dst)for(size_t src=0;src<=10;++src)for(size_t n=0;n<=10;++n){
        uint8_t actual[12],expected[12];for(unsigned k=0;k<12;++k)actual[k]=expected[k]=(uint8_t)k;
        bool valid=dst<=10 && src<=10 && n<=10-dst && n<=10-src;
        if(valid)memmove(expected+dst,expected+src,n);
        CHECK(move_bytes(actual,10,dst,src,n)==valid);
        CHECK(memcmp(actual,expected,12)==0);
    }
    uint8_t safe[4]={1,2,3,4};
    CHECK(!move_bytes(safe,4,SIZE_MAX,0,1));
    CHECK(!move_bytes(safe,4,0,0,SIZE_MAX));
    CHECK(!move_bytes(NULL,0,0,0,0));
    printf("PASS: %lu assertions; defined examples + boundary/property tests.\n",checks);
    return 0;
}
