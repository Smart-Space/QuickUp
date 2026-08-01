#include <vector>
#include <string>
#include <cstdint>
#include <cctype>

void utf8_to_codepoints(const char* str, size_t len, std::vector<uint32_t>& codepoints) {
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
        codepoints.push_back(ch);
    }
}

int computeOrderedMatchLen(const std::vector<uint32_t>& query, const std::vector<uint32_t>& candidate) {
    if (query.empty()) {
        return 0;
    }
    size_t qi = 0;
    const size_t qn = query.size();
    const size_t cn = candidate.size();
    for (size_t ci = 0; ci < cn && qi < qn; ++ci) {
        if (candidate[ci] == query[qi]) {
            qi++;
        }
        // 剪枝：剩余候选字符不足以匹配剩余查询字符
        if ((cn - ci - 1) < (qn - qi)) {
            break;
        }
    }
    return static_cast<int>(qi);
}
