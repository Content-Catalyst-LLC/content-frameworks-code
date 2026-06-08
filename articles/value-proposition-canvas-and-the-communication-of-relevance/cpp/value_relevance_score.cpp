#include <iostream>
#include <iomanip>

int main() {
    double score = (0.91 + 0.84 + 0.86 + 0.76 + 0.90 + 0.88) / 6.0;
    std::cout << "Value relevance score: " << std::fixed << std::setprecision(3) << score << "\n";
    return 0;
}
