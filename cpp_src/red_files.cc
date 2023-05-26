#include <fstream>
#include "json/single_include/nlohmann/json.hpp"
#include <iostream>


int main() {
    // int num_opportunities = 4;

    // // 1 - фоткаем, - 0 сбрасываем
    // std::vector<double> priorities = {1, 0, 0, 0}; // Priority weights

    // // Штраф за то что храним данные на спутнике
    // // std::vector<double> d(num_opportunities, 1.0);

    // std::vector<double> opportunity_memory_sizes = {7, 7, 1, 3};

    // // Это сеты в которых записано то что мы делаем
    // std::vector<int> s_img = {0};
    // std::vector<int> s_dl = {1,2,3};

    std::vector<std::vector<int>> s_mutex;

    // std::vector<int> op_sat_id = {0,0,0,0};
    // std::unordered_map<int, std::vector<int>> op_sat_id_dict = { {0,{0,1,2,3}} };
    // double alpha = 0.001;

    // // capacity
    // std::vector<int> cap = {10,10,10,10};

    std::ifstream f_img("s_img.json");
    nlohmann::ordered_json s_img_json = nlohmann::ordered_json::parse(f_img);

    std::ifstream f_mutex("s_mutex.json");
    nlohmann::ordered_json s_mutex_json = nlohmann::ordered_json::parse(f_mutex);

    std::ifstream f_dl("s_dl.json");
    nlohmann::ordered_json s_dl_json = nlohmann::ordered_json::parse(f_dl);

    std::ifstream f_priorities("priorities.json");
    nlohmann::ordered_json priorities_json = nlohmann::ordered_json::parse(f_priorities);

    std::ifstream f_cap_sat_list("cap_sat_list.json");
    nlohmann::ordered_json cap_sat_list_json = nlohmann::ordered_json::parse(f_cap_sat_list);

    std::ifstream f_op_sat_id("op_sat_id.json");
    nlohmann::ordered_json op_sat_id_json = nlohmann::ordered_json::parse(f_op_sat_id);

    std::ifstream f_op_sat_id_dict("op_sat_id_dict.json");
    nlohmann::ordered_json op_sat_id_dict_json = nlohmann::ordered_json::parse(f_op_sat_id_dict);

    std::ifstream f_opportunity_memory_sizes("opportunity_memory_sizes.json");
    nlohmann::ordered_json opportunity_memory_sizes_json = nlohmann::ordered_json::parse(f_opportunity_memory_sizes);

    std::vector<int> s_dl;
    std::vector<int> s_img;
    std::vector<double> cap_sat_list;
    std::vector<double> priorities;
    std::vector<double> opportunity_memory_sizes;
    std::unordered_map<std::string, std::vector<int>> op_sat_id_dict;
    std::vector<std::string> op_sat_id;
    int num_opportunities;
    double alpha = 0.001;


    for (auto& el : op_sat_id_dict_json.items()) {
        std::cout << el.key() << std::endl;
        std::vector<int> d_values;
        for (auto& el_arr : el.value()) {
            // std::cout << el_arr << std::endl;
            d_values.push_back(el_arr);
        }
        op_sat_id_dict[el.key()] = d_values;
    }


    for (auto& el : priorities_json.items()) {
        // std::cout << el.value() << std::endl;
        priorities.push_back(el.value());
    }

    for (auto& el : cap_sat_list_json.items()) {
        // std::cout << el.value() << std::endl;
        cap_sat_list.push_back(el.value());
    }

    for (auto& el : opportunity_memory_sizes_json.items()) {
        // std::cout << el.value() << std::endl;
        opportunity_memory_sizes.push_back(el.value());
    }


    for (auto& el : op_sat_id_json.items()) {
        // std::cout << el.value() << std::endl;
        op_sat_id.push_back(el.value());
    }

    for (auto& el : s_dl_json.items()) {
        // std::cout << el.value() << std::endl;
        s_dl.push_back(el.value());
    }

    for (auto& el : s_img_json.items()) {
        // std::cout << el.value() << std::endl;
        s_img.push_back(el.value());
    }

    num_opportunities = priorities.size();




// int main(){
//     std::ifstream f_img("s_img.json");
//     nlohmann::ordered_json s_img_json = nlohmann::ordered_json::parse(f_img);

//     std::ifstream f_mutex("s_mutex.json");
//     nlohmann::ordered_json s_mutex_json = nlohmann::ordered_json::parse(f_mutex);

//     std::ifstream f_dl("s_dl.json");
//     nlohmann::ordered_json s_dl_json = nlohmann::ordered_json::parse(f_dl);

//     std::ifstream f_priorities("priorities.json");
//     nlohmann::ordered_json priorities_json = nlohmann::ordered_json::parse(f_priorities);

//     std::ifstream f_cap_sat_list("cap_sat_list.json");
//     nlohmann::ordered_json cap_sat_list_json = nlohmann::ordered_json::parse(f_cap_sat_list);

//     std::ifstream f_op_sat_id("op_sat_id.json");
//     nlohmann::ordered_json op_sat_id_json = nlohmann::ordered_json::parse(f_op_sat_id);

//     std::ifstream f_op_sat_id_dict("op_sat_id_dict.json");
//     nlohmann::ordered_json op_sat_id_dict_json = nlohmann::ordered_json::parse(f_op_sat_id_dict);

//     std::ifstream f_opportunity_memory_sizes("opportunity_memory_sizes.json");
//     nlohmann::ordered_json opportunity_memory_sizes_json = nlohmann::ordered_json::parse(f_opportunity_memory_sizes);

//     std::vector<int> s_dl;
//     std::vector<int> s_img;
//     std::vector<double> cap_sat_list;
//     std::vector<int> priorities;
//     std::vector<double> opportunity_memory_sizes;
//     std::unordered_map<std::string, std::vector<int>> op_sat_id_dict;
//     std::vector<std::string> op_sat_id;


//     for (auto& el : op_sat_id_dict_json.items()) {
//         std::cout << el.key() << std::endl;
//         std::vector<int> d_values;
//         for (auto& el_arr : el.value()) {
//             // std::cout << el_arr << std::endl;
//             d_values.push_back(el_arr);
//         }
//         op_sat_id_dict[el.key()] = d_values;
//     }


//     for (auto& el : priorities_json.items()) {
//         // std::cout << el.value() << std::endl;
//         priorities.push_back(el.value());
//     }

//     for (auto& el : cap_sat_list_json.items()) {
//         // std::cout << el.value() << std::endl;
//         cap_sat_list.push_back(el.value());
//     }

//     for (auto& el : opportunity_memory_sizes_json.items()) {
//         // std::cout << el.value() << std::endl;
//         opportunity_memory_sizes.push_back(el.value());
//     }


//     for (auto& el : op_sat_id_json.items()) {
//         // std::cout << el.value() << std::endl;
//         op_sat_id.push_back(el.value());
//     }

//     for (auto& el : s_dl_json.items()) {
//         // std::cout << el.value() << std::endl;
//         s_dl.push_back(el.value());
//     }

//     for (auto& el : s_img_json.items()) {
//         // std::cout << el.value() << std::endl;
//         s_img.push_back(el.value());
//     }
    
//     std::cout << op_sat_id[10]<< std::endl;
// }
