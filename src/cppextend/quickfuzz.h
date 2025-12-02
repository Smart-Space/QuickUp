#include <vector>
#include <string>
#include <cstdint>

std::vector<uint32_t> utf8_to_codepoints(const std::string& str) {
    std::vector<uint32_t> res;
    size_t i = 0;
    while (i < str.size()) {
        uint8_t c = static_cast<uint8_t>(str[i]);
        if (c <= 0x7F) {
            res.push_back(c);
            i++;
        } else if ((c & 0xE0) == 0xC0) {
            if (i + 1 >= str.size()) break;
            uint32_t ch = (c & 0x1F) << 6;
            ch |= static_cast<uint8_t>(str[i+1]) & 0x3F;
            res.push_back(ch);
            i += 2;
        } else if ((c & 0xF0) == 0xE0) {
            if (i + 2 >= str.size()) break;
            uint32_t ch = (c & 0x0F) << 12;
            ch |= (static_cast<uint8_t>(str[i+1]) & 0x3F) << 6;
            ch |= static_cast<uint8_t>(str[i+2]) & 0x3F;
            res.push_back(ch);
            i += 3;
        } else if ((c & 0xF8) == 0xF0) {
            if (i + 3 >= str.size()) break;
            uint32_t ch = (c & 0x07) << 18;
            ch |= (static_cast<uint8_t>(str[i+1]) & 0x3F) << 12;
            ch |= (static_cast<uint8_t>(str[i+2]) & 0x3F) << 6;
            ch |= static_cast<uint8_t>(str[i+3]) & 0x3F;
            res.push_back(ch);
            i += 4;
        } else {
            i++;
        }
    }
    return res;
}

int computeLCS(const std::vector<uint32_t>& a, const std::vector<uint32_t>& b) {
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
        for (int j = 1; j <= m; ++j) {
            int temp = dp[j];
            if (longer->at(i-1) == shorter->at(j-1)) {
                dp[j] = prev_diag_val + 1;
            } else {
                dp[j] = std::max(dp[j-1], dp[j]);
            }
            prev_diag_val = temp;
        }
    }
    return dp[m];
}

std::vector<uint32_t> target_chars;
int target_len = 0;
void setTargetChars(const std::string& str) {
    target_chars = utf8_to_codepoints(str);
    target_len = target_chars.size();
}

int calculateSimilarity(const std::string& b) {
    std::vector<uint32_t> b_chars = utf8_to_codepoints(b);
    if (target_len == 0) return 0;
    int lcs_length = computeLCS(target_chars, b_chars);
    return (lcs_length * 100) / target_len;
}
