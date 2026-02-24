#include <vector>
#include <string>
#include <cstdint>

std::vector<uint32_t> utf8_to_codepoints(const char* str, size_t len) {
    std::vector<uint32_t> res;
    res.reserve(len);
    size_t i = 0;
    while (i < len) {
        uint8_t c = static_cast<uint8_t>(str[i]);
        uint32_t ch = 0;
        if (c <= 0x7F) {
            ch = c;
            i++;
        } else if ((c & 0xE0) == 0xC0) {
            if (i + 1 >= len) break;
            ch = (c & 0x1F) << 6 | static_cast<uint8_t>(str[i+1]) & 0x3F;
            i += 2;
        } else if ((c & 0xF0) == 0xE0) {
            if (i + 2 >= len) break;
            ch = (c & 0x0F) << 12;
            ch |= (static_cast<uint8_t>(str[i+1]) & 0x3F) << 6;
            ch |= static_cast<uint8_t>(str[i+2]) & 0x3F;
            i += 3;
        } else if ((c & 0xF8) == 0xF0) {
            if (i + 3 >= len) break;
            ch = (c & 0x07) << 18;
            ch |= (static_cast<uint8_t>(str[i+1]) & 0x3F) << 12;
            ch |= (static_cast<uint8_t>(str[i+2]) & 0x3F) << 6;
            ch |= static_cast<uint8_t>(str[i+3]) & 0x3F;
            i += 4;
        } else {
            i++;
        }
        if (ch < 128) {
            // 仅处理英文大小写
            ch = std::tolower(ch);
        }
        res.push_back(ch);
    }
    return res;
}

int computeLCS(const std::vector<uint32_t>& a, const std::vector<uint32_t>& b, int min_required_len) {
    const std::vector<uint32_t>* shorter = &a;
    const std::vector<uint32_t>* longer = &b;
    if (a.size() > b.size()) {
        shorter = &b;
        longer = &a;
    }
    const int m = shorter->size();
    const int n = longer->size();
    std::vector<int> dp(m+1, 0);
    for (int i = 1; i <= n; ++i) {
        int prev_diag_val = 0;
        uint32_t longer_char = longer->at(i-1);
        for (int j = 1; j <= m; ++j) {
            int temp = dp[j];
            if (longer_char == shorter->at(j-1)) {
                dp[j] = prev_diag_val + 1;
            } else {
                dp[j] = std::max(dp[j-1], dp[j]);
            }
            prev_diag_val = temp;
        }
        if (dp[m] >= min_required_len) {
            // found a match
            return dp[m];
        }
        if (dp[m] + (n-i) < min_required_len) {
            // no chance of finding a match
            return -1;
        }
    }
    return dp[m];
}

std::vector<uint32_t> target_chars;
int target_len = 0;
int lcs_acc = 0;
void setTargetChars(const char* str, size_t len, int acc) {
    target_chars = utf8_to_codepoints(str, len);
    target_len = target_chars.size();
    lcs_acc = acc;
}

int calculateSimilarity(const char* b, size_t b_len) {
    if (target_len == 0) return 0;
    std::vector<uint32_t> b_chars = utf8_to_codepoints(b, b_len);
    int min_lcs_needed = (lcs_acc * target_len + 99) / 100; 
    int lcs_length = computeLCS(target_chars, b_chars, min_lcs_needed);
    if (lcs_length == -1) return 0;
    return (lcs_length * 100) / target_len;
}
