//
// Created by jinhai on 23-3-6.
//

#pragma once

#include "planner/logical_node.h"

namespace infinity {

class LogicalDropSchema final : public LogicalNode {
public:
    LogicalDropSchema(u64 node_id,
                      SharedPtr<String> schema_name,
                      ConflictType conflict_type)
            : LogicalNode(node_id, LogicalNodeType::kDropSchema),
              schema_name_(std::move(schema_name)),
              conflict_type_(conflict_type)
    {}

    [[nodiscard]] inline Vector<ColumnBinding>
    GetColumnBindings() const final {
        return {};
    }

    [[nodiscard]] inline SharedPtr<Vector<String>>
    GetOutputNames() const final {
        return MakeShared<Vector<String>>();
    }

    String
    ToString(i64& space) final;

    inline String
    name() final {
        return "LogicalDropSchema";
    }

    [[nodiscard]] SharedPtr<String>
    schema_name() const {
        return schema_name_;
    }

    [[nodiscard]] ConflictType
    conflict_type() const {
        return conflict_type_;
    }

private:
    SharedPtr<String> schema_name_{};
    ConflictType conflict_type_{ConflictType::kInvalid};
};

}