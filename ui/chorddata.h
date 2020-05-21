#include <map>
#include <regex>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

#ifndef CHORD_H
#define CHORD_H

class ChordData {
public:
    ChordData() = default;
    explicit ChordData(const std::string &chord);
    explicit ChordData(const std::string &root, const std::string &quality);

    explicit operator std::string() const;

    std::vector<int> components();

    static std::unordered_map<std::string, int> note_values;
private:
    std::tuple<std::string, std::string> chord_data_;

    static std::regex pattern_;
    static std::unordered_map<std::string, std::vector<int>> components_;
};

#endif //CHORD_H
