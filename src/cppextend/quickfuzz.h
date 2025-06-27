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
    int m = a.size();
    int n = b.size();
    std::vector<std::vector<int>> dp(m + 1, std::vector<int>(n + 1, 0));
    for (int i = 1; i <= m; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (a[i-1] == b[j-1]) {
                dp[i][j] = dp[i-1][j-1] + 1;
            } else {
                dp[i][j] = std::max(dp[i-1][j], dp[i][j-1]);
            }
        }
    }
    return dp[m][n];
}

int calculateSimilarity(const std::string& a, const std::string& b) {
    std::vector<uint32_t> a_chars = utf8_to_codepoints(a);
    std::vector<uint32_t> b_chars = utf8_to_codepoints(b);
    int a_len = a_chars.size();
    if (a_len == 0) return 0;
    int lcs_length = computeLCS(a_chars, b_chars);
    return (lcs_length * 100) / a_len;
}
