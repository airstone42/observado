#include "chorddata.h"

#include <algorithm>
#include <stdexcept>

std::regex ChordData::pattern_("([A-G|a-g][#|b]?)([7|maj7]?sus[2|4]?|ø7?|mmaj7|maj7|m|9|11|13|[aug|dim]?[7|maj7]?)");

std::unordered_map<std::string, int> ChordData::note_values({ { "C", 0 },
    { "C#", 1 },
    { "Db", 1 },
    { "D", 2 },
    { "D#", 3 },
    { "Eb", 3 },
    { "E", 4 },
    { "F", 5 },
    { "F#", 6 },
    { "Gb", 6 },
    { "G", 7 },
    { "G#", 8 },
    { "Ab", 8 },
    { "A", 9 },
    { "A#", 10 },
    { "Bb", 10 },
    { "B", 11 } });

std::unordered_map<std::string, std::vector<int>> ChordData::components_({ { "M", { 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0 } },
    { "m", { 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0 } },
    { "7", { 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0 } },
    { "m7", { 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0 } },
    { "maj7", { 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1 } } });

ChordData::ChordData(const std::string &root, const std::string &quality)
    : chord_data_(root, quality)
{
}

ChordData::ChordData(const std::string &chord)
{
    std::smatch match;
    if (std::regex_search(chord, match, pattern_))
        if (match.size() == 3)
            chord_data_ = std::make_tuple(match[1], match[2]);
}

std::vector<int> ChordData::components()
{
    try {
        auto [root, quality] = chord_data_;
        int roll = note_values.at(root);
        auto compo = components_.at(quality.empty() ? "M" : quality);
        std::rotate(compo.rbegin(), compo.rbegin() + roll, compo.rend());
        return compo;
    } catch (const std::out_of_range &) {
        return std::vector<int>();
    }
}

ChordData::operator std::string() const
{
    auto [root, quality] = chord_data_;
    return std::string(root + quality);
}
