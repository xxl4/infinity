//
// Created by jinhai on 23-3-8.
//
#include <gtest/gtest.h>
#include "base_test.h"
#include "common/column_vector/column_vector.h"
#include "common/types/value.h"
#include "main/logger.h"
#include "main/stats/global_resource_usage.h"
#include "main/session.h"
#include "planner/logical_planner.h"
#include "planner/optimizer.h"
#include "executor/physical_planner.h"
#include "scheduler/operator_pipeline.h"
#include "main/infinity.h"
#include "bin/compilation_config.h"
#include "test_helper/sql_runner.h"

#include "main/profiler/show_logical_plan.h"
#include "parser/sql_parser.h"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <streambuf>

class LogicalPlannerTpchTest : public BaseTest {
    void
    SetUp() override {
        infinity::GlobalResourceUsage::Init();
        infinity::Infinity::instance().Init();
    }

    void
    TearDown() override {
        infinity::Infinity::instance().UnInit();
        EXPECT_EQ(infinity::GlobalResourceUsage::GetObjectCount(), 0);
        EXPECT_EQ(infinity::GlobalResourceUsage::GetRawMemoryCount(), 0);
        infinity::GlobalResourceUsage::UnInit();
    }
};

TEST_F(LogicalPlannerTpchTest, test1) {
    using namespace infinity;

    // Create tables;
    {
        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/create.sql";
        std::ifstream t(ddl_sql.c_str());
        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
        SQLRunner::Run(input_sql, false);
    }

    // Show tables
    {
        SQLRunner::Run("show tables;", false);
    }

//    // Insert CUSTOMER table
//    {
//        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_customer.sql";
//        std::ifstream t(ddl_sql.c_str());
//        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
//        SQLRunner::Run(input_sql, false);
//    }
//
//    // Insert LINEITEM table
//    {
//        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_lineitem.sql";
//        std::ifstream t(ddl_sql.c_str());
//        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
//        SQLRunner::Run(input_sql, false);
//    }
//
//    // Insert NATION table
//    {
//        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_nation.sql";
//        std::ifstream t(ddl_sql.c_str());
//        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
//        SQLRunner::Run(input_sql, false);
//    }

//    // Insert ORDERS table
//    {
//        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_orders.sql";
//        std::ifstream t(ddl_sql.c_str());
//        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
//        SQLRunner::Run(input_sql, false);
//    }

    // Insert PARTS table
    {
        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_parts.sql";
        std::ifstream t(ddl_sql.c_str());
        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
        SQLRunner::Run(input_sql, false);
    }

    // Insert PARTSUPP table
    {
        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_partsupp.sql";
        std::ifstream t(ddl_sql.c_str());
        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
        SQLRunner::Run(input_sql, false);
    }

    // Insert REGION table
    {
        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_region.sql";
        std::ifstream t(ddl_sql.c_str());
        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
        SQLRunner::Run(input_sql, false);
    }

    // Insert SUPPLIER table
    {
        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/insert_supplier.sql";
        std::ifstream t(ddl_sql.c_str());
        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
        SQLRunner::Run(input_sql, false);
    }

    // DROP tables;
    {
        String ddl_sql = String(TEST_DATA_PATH) + "/tpch/drop.sql";
        std::ifstream t(ddl_sql.c_str());
        String input_sql((std::istreambuf_iterator<char>(t)), std::istreambuf_iterator<char>());
        SQLRunner::Run(input_sql, false);
    }
}