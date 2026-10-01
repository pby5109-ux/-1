#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>

/* Automatically extracted from answer blocks; edit JSON source first. */

/* C09 */
uint64_t square_sample(volatile const uint32_t *p) {
    uint32_t sample = *p;
    return (uint64_t)sample * sample;
}

/* C43 */
uint8_t reverse8(uint8_t x) {
    uint8_t r = 0;
    for (unsigned i = 0; i < 8; ++i) {
        r = (uint8_t)((r << 1) | (x & 1U));
        x = (uint8_t)(x >> 1);
    }
    return r;
}

/* C44 */
bool reverse_text(char *s) {
    if (s == NULL) return false;
    size_t left = 0, right = strlen(s);
    while (left < right) {
        --right;
        if (left >= right) break;
        char t = s[left];
        s[left++] = s[right];
        s[right] = t;
    }
    return true;
}

/* C45 */
bool longest_digits(const char *s, size_t *start, size_t *len) {
    if (s == NULL || start == NULL || len == NULL) return false;
    size_t best_start = SIZE_MAX, best_len = 0, i = 0;
    while (s[i] != '\0') {
        if (s[i] < '0' || s[i] > '9') { ++i; continue; }
        size_t begin = i;
        while (s[i] >= '0' && s[i] <= '9') ++i;
        size_t run = i - begin;
        if (run > best_len) { best_start = begin; best_len = run; }
    }
    *start = best_start;
    *len = best_len;
    return true;
}

/* C46 */
bool is_prime(uint32_t n) {
    if (n < 2) return false;
    for (uint32_t i = 2; i <= n / i; ++i) {
        if (n % i == 0) return false;
    }
    return true;
}

/* C47 */
uint32_t swap32(uint32_t x) {
    return ((x & UINT32_C(0x000000FF)) << 24) |
           ((x & UINT32_C(0x0000FF00)) << 8) |
           ((x & UINT32_C(0x00FF0000)) >> 8) |
           ((x & UINT32_C(0xFF000000)) >> 24);
}

/* C48 */
static bool ascii_alnum(unsigned char c) {
    return (c >= '0' && c <= '9') ||
           (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}
static unsigned char ascii_lower(unsigned char c) {
    return (c >= 'A' && c <= 'Z')
        ? (unsigned char)(c + ('a' - 'A')) : c;
}
bool palindrome(const char *s) {
    if (s == NULL) return false;
    size_t l = 0, r = strlen(s);
    while (l < r) {
        if (!ascii_alnum((unsigned char)s[l])) { ++l; continue; }
        if (!ascii_alnum((unsigned char)s[r - 1])) { --r; continue; }
        if (ascii_lower((unsigned char)s[l]) !=
            ascii_lower((unsigned char)s[r - 1])) return false;
        ++l;
        --r;
    }
    return true;
}

/* C49 */
bool copy_text(char *dst, size_t cap, const char *src) {
    if (dst == NULL || src == NULL || cap == 0) return false;
    size_t n = strlen(src);
    if (n >= cap) return false;
    memcpy(dst, src, n + 1);
    return true;
}

/* C50 */
bool move_bytes(uint8_t *buf, size_t cap, size_t dst,
                size_t src, size_t n) {
    if (buf == NULL || dst > cap || src > cap ||
        n > cap - dst || n > cap - src) return false;
    if (dst <= src) {
        for (size_t i = 0; i < n; ++i) buf[dst+i] = buf[src+i];
    } else {
        for (size_t i = n; i > 0; --i) buf[dst+i-1] = buf[src+i-1];
    }
    return true;
}
