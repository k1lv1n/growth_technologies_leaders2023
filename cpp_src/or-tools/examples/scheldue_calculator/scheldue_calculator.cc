#include <iostream>
#include <memory>
#include <vector>
#include <fstream>
#include <sstream>  // для использования std::stringstream
#include <string>
#include "json/single_include/nlohmann/json.hpp"
// #include "or-tools/include/ortools/linear_solver/linear_solver.h"
#include "ortools/linear_solver/linear_solver.h"



// std::vector<std::pair<int, int>> get_pairs(std::pair<const std::string, std::vector<int>> s) {
//     std::vector<std::pair<int, int>> res;
//     int n = s.size();
//     for (int i = 0; i < n; i++) {
//         for (int j = i + 1; j < n; j++) {
//             res.push_back({s[i], s[j]});
//         }
//     }
//     return res;
// }


std::vector<std::pair<int, int>> get_pairs(const std::pair<const std::string, std::vector<int>>& s) {
    std::vector<std::pair<int, int>> result;
    const std::vector<int>& v = s.second;
    for (int i = 0; i < v.size(); i++) {
        for (int j = i + 1; j < v.size(); j++) {
            result.emplace_back(v[i], v[j]);
        }
    }
    return result;
}


int prev_con_id(int con_id, std::vector<std::string> op_sat_id, std::unordered_map<std::string, std::vector<int>> op_sat_id_dict) {
    int prev_con = -1;
    std::string sat_key = op_sat_id[con_id];
    std::vector<int> v = op_sat_id_dict[sat_key];
    for (int i = 0; i < v.size(); i++) {
        if (v[i] == con_id) break;
        prev_con = v[i];
    }
    return prev_con;
}


std::unordered_map<std::string, int> cond_for_moment_i(int con_id, std::unordered_map<std::string, std::vector<int>> op_sat_id_dict) {
    auto find_position = [](std::vector<int> arr, int new_elem) -> int {
        int left = 0;
        int right = arr.size() - 1;
        while (left <= right) {
            int mid = (left + right) / 2;
            if (new_elem == arr[mid]) return mid;
            else if (new_elem < arr[mid]) right = mid - 1;
            else left = mid + 1;
        }
        return left;
    };

    std::unordered_map<std::string, int> res;
    for (auto& k : op_sat_id_dict) {
        std::vector<int> v = op_sat_id_dict[k.first];
        int pos = find_position(v, con_id);
        if (pos == 0) {
            if (v[0] <= con_id)
                res[k.first] = v[0];
        } else {
            if ((pos == v.size()) || (con_id < v[pos]))
                res[k.first] = v[pos - 1];
            else
                res[k.first] = v[pos];
        }
    }
    return res;
}


void calculate(
                int num_opportunities,
                std::vector<double> cap,
                std::unordered_map<std::string, std::vector<int>> s_mutex,
                std::vector<int> s_img,
                std::vector<int> s_dl,
                std::vector<std::string> op_sat_id,
                std::unordered_map<std::string, std::vector<int>> op_sat_id_dict,
                std::vector<double> opportunity_memory_sizes,
                double alpha,
                std::vector<double> priorities
                ) {
    
    // std::unique_ptr<operations_research::MPSolver> solver(operations_research::MPSolver::CreateSolver("GLOP"));
    auto env = absl::make_unique<operations_research::MPSolver>("Satellite", operations_research::MPSolver::CLP_LINEAR_PROGRAMMING);
    // solver.
    auto solver = env.get();
    auto status_threads= solver->SetNumThreads(12);
    LOG(INFO) << "Solution:" << status_threads;
    if (!solver) {
        LOG(WARNING) << "CLP_LINEAR_PROGRAMMING solver unavailable.";
        return;
    }

    // auto env = absl::make_unique<operations_research::MPSolver>("Satellite", operations_research::MPSolver::CLP_LINEAR_PROGRAMMING);
    // auto solver = env.get();

    std::vector<operations_research::MPVariable*> x(num_opportunities);
    std::vector<operations_research::MPVariable*> y(num_opportunities);

    for (int i = 0; i < num_opportunities; i++) {
        x[i] = solver->MakeNumVar(0.0, 1.0, "x_" + std::to_string(i));
        y[i] = solver->MakeNumVar(0, cap[i], "y_" + std::to_string(i));
    }
    LOG(INFO) << "Number of variables = " << solver->NumVariables();

    for (auto& el : s_mutex) {
        for (auto& [l, r] : get_pairs(el)) {
            operations_research::MPConstraint* const ct_mutex = solver->MakeRowConstraint(0.0, 1.0, "ct_mutex");
            ct_mutex->SetCoefficient(x[l], 1);
            ct_mutex->SetCoefficient(x[r], 1);
            }
        }
    

    int s_img_size = s_img.size();
    int s_dl_size = s_dl.size();
    auto objective = solver->MutableObjective();
    const double infinity = solver->infinity();

    for (int i = 0; i < num_opportunities; i++) {
        int pr_con_id = prev_con_id(i, op_sat_id, op_sat_id_dict);
        operations_research::MPVariable* tmp = 0;
        if (pr_con_id != -1) tmp = y[pr_con_id];

        if ((std::find(s_img.begin(), s_img.end(), i) != s_img.end())) {
            operations_research::MPConstraint* const ct_img = solver->MakeRowConstraint(0.0, 0.0, "ct_img");
            ct_img->SetCoefficient(tmp, 1);
            ct_img->SetCoefficient(x[i], opportunity_memory_sizes[i]);
            ct_img->SetCoefficient(y[i], -1);
        }
        if ((std::find(s_dl.begin(), s_dl.end(), i) != s_dl.end())) {
            operations_research::MPConstraint* const ct_dl_1 = solver->MakeRowConstraint(-infinity, 0, "ct_dl_1");
            ct_dl_1->SetCoefficient(y[i], -1);
            ct_dl_1->SetCoefficient(tmp, 1);
            ct_dl_1->SetCoefficient(x[i], -opportunity_memory_sizes[i]);

            operations_research::MPConstraint* const ct_dl_2 = solver->MakeRowConstraint(0, infinity, "ct_dl_2");
            ct_dl_1->SetCoefficient(y[i], -1);
            ct_dl_2->SetCoefficient(tmp, 1);
        }

        double val = 0;

        // for (auto& [k, v] : cond_for_moment_i(i, op_sat_id_dict)) {
        //     val += y[v]->solution_value() * alpha * 1;
        //     LOG(INFO) << "k:" << k;
        //     LOG(INFO) << "v:" << k;
        //     LOG(INFO) << "val:" << val;
        // }
        objective->SetCoefficient(x[i], -priorities[i]);
        objective->SetCoefficient(y[i], alpha * 1);
    }
    objective->SetMinimization();

    solver->Solve();

    LOG(INFO) << "Solution:" << std::endl;
    LOG(INFO) << "Objective value = " << objective->Value();
    for (int i = 0; i < num_opportunities; i++) {
        std::string log_string = "";
        log_string += "x_" + std::to_string(i) + "=" + std::to_string(x[i]->solution_value()) + " ";
        log_string += "y_" + std::to_string(i) + "=" + std::to_string(y[i]->solution_value()) + " ";
        LOG(INFO) << log_string;
    }

    // std::vector<int> transfered_data(num_opportunities, 0);
    // int s_prev = 0;

    // for (int i = 0; i < num_opportunities; i++) {
    //     std::unordered_map<int, int> moments = cond_for_moment_i(i, op_sat_id_dict);
    //     int s = 0;
    //     for (auto& [k, v] : moments) {
    //         if (y[v]->solution_value()) {
    //             s += 1;
    //         }
    //     }
    //     if ((s_prev != s) && (x[i]->solution_value() > 0)) {
    //         transfered_data[i] = s - s_prev;
    //         s_prev = s;
    //     } else {
    //         transfered_data[i] = 0;
    //     }
    // }
    
    // for (int i = 0; i < transfered_data.size(); i++) {
    //     std::cout << transfered_data[i] << " ";
    // }
    // std::cout << std::endl;
}


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

    // std::vector<std::vector<int>> s_mutex;

    // std::vector<int> op_sat_id = {0,0,0,0};
    // std::unordered_map<int, std::vector<int>> op_sat_id_dict = { {0,{0,1,2,3}} };
    // double alpha = 0.001;

    // // capacity
    // std::vector<int> cap = {10,10,10,10};

    std::ifstream f_img("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/s_img.json");
    nlohmann::ordered_json s_img_json = nlohmann::ordered_json::parse(f_img);

    std::ifstream f_mutex("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/s_mutex.json");
    nlohmann::ordered_json s_mutex_json = nlohmann::ordered_json::parse(f_mutex);

    std::ifstream f_dl("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/s_dl.json");
    nlohmann::ordered_json s_dl_json = nlohmann::ordered_json::parse(f_dl);

    std::ifstream f_priorities("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/priorities.json");
    nlohmann::ordered_json priorities_json = nlohmann::ordered_json::parse(f_priorities);

    std::ifstream f_cap_sat_list("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/cap_sat_list.json");
    nlohmann::ordered_json cap_sat_list_json = nlohmann::ordered_json::parse(f_cap_sat_list);

    std::ifstream f_op_sat_id("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/op_sat_id.json");
    nlohmann::ordered_json op_sat_id_json = nlohmann::ordered_json::parse(f_op_sat_id);

    std::ifstream f_op_sat_id_dict("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/op_sat_id_dict.json");
    nlohmann::ordered_json op_sat_id_dict_json = nlohmann::ordered_json::parse(f_op_sat_id_dict);

    std::ifstream f_opportunity_memory_sizes("/root/growth_technologies_leaders2023/cpp_src/or-tools/examples/scheldue_calculator/opportunity_memory_sizes.json");
    nlohmann::ordered_json opportunity_memory_sizes_json = nlohmann::ordered_json::parse(f_opportunity_memory_sizes);

    std::vector<int> s_dl;
    std::vector<int> s_img;
    std::vector<double> cap_sat_list;
    std::vector<double> priorities;
    std::vector<double> opportunity_memory_sizes;
    std::unordered_map<std::string, std::vector<int>> op_sat_id_dict;
    std::vector<std::string> op_sat_id;
    std::unordered_map<std::string, std::vector<int>> s_mutex;
    int num_opportunities;
    double alpha = 0.00001;


    for (auto& el : op_sat_id_dict_json.items()) {
        // std::cout << el.key() << std::endl;
        std::vector<int> d_values;
        for (auto& el_arr : el.value()) {
            // std::cout << el_arr << std::endl;
            d_values.push_back(el_arr);
        }
        op_sat_id_dict[el.key()] = d_values;
    }

    for (auto& el : s_mutex_json.items()) {
        std::cout << el.key() << std::endl;
        std::vector<int> d_values;
        for (auto& el_arr : el.value()) {
            // std::cout << el_arr << std::endl;
            d_values.push_back(el_arr);
        }
        s_mutex[el.key()] = d_values;
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

    calculate(
        num_opportunities,
        cap_sat_list,
        s_mutex,
        s_img,
        s_dl,
        op_sat_id,
        op_sat_id_dict,
        opportunity_memory_sizes,
        alpha,
        priorities

    );
}