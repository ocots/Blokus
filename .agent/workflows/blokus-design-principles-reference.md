# Design Principles & Quality Objectives Reference

**Version**: 1.0  
**Last Updated**: 2025-12-31  
**Purpose**: Central reference for software design principles and quality objectives used across all workflows

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [SOLID Principles](#solid-principles)
3. [Other Design Principles](#other-design-principles)
4. [Quality Objectives](#quality-objectives)
5. [Julia-Specific Considerations](#julia-specific-considerations)
6. [Quick Reference Checklists](#quick-reference-checklists)
7. [References](#references)

---

## Introduction

This document provides a comprehensive reference for software design principles and quality objectives. These principles are universal and apply to any programming paradigm, including Julia's multiple dispatch approach.

**When to use this document**:
- During planning (`/planning` workflow)
- When analyzing PRs (`/pr-action-plan`, `/pr-code-review`)
- When reviewing issues (`/issue-status-report`)
- When writing tests (`/test-julia`)

**Key Philosophy**: Good design is not about following rules blindly, but about understanding trade-offs and making informed decisions.

---

## SOLID Principles

SOLID is an acronym for five design principles that make software more understandable, flexible, and maintainable.

### S - Single Responsibility Principle (SRP)

**Definition**: Every module, function, and type should have a single, well-defined responsibility. There should be only one reason to change it.

**Benefits**:
- Easier to understand and test
- Smaller, more focused components
- Reduced coupling
- Easier to maintain and modify

**Julia Examples**:

✅ **Good** - Each function has one clear purpose:
```julia
# Parsing responsibility
function parse_ocp_input(text::String)
    # Only handles parsing logic
    return parsed_data
end

# Validation responsibility
function validate_ocp_data(data)
    # Only handles validation logic
    return is_valid, errors
end

# Processing responsibility
function solve_ocp(data)
    # Only handles solving logic
    return solution
end
```

❌ **Bad** - Function does too many things:
```julia
function handle_ocp(text::String)
    # Parsing
    parsed = parse(text)
    
    # Validation
    if !isvalid(parsed)
        throw(ArgumentError("Invalid input"))
    end
    
    # Processing
    solution = solve(parsed)
    
    # I/O
    save_to_file(solution, "output.txt")
    
    # Formatting
    return format_output(solution)
end
```

**How to Apply in Julia**:
- Keep functions focused on one task
- Separate concerns: parsing, validation, computation, I/O
- Use multiple dispatch to separate different behaviors
- Create small, composable functions

**Red Flags**:
- Function names with "and" or "or" (e.g., `parse_and_validate`)
- Functions longer than 50 lines
- Functions with multiple `if-else` branches handling different concerns
- Modules that mix unrelated functionality

---

### O - Open/Closed Principle (OCP)

**Definition**: Software entities should be open for extension but closed for modification. You should be able to add new functionality without changing existing code.

**Benefits**:
- Existing code remains stable
- New features don't break old functionality
- Easier to maintain and test
- Promotes reusability

**Julia Examples**:

✅ **Good** - Using abstract types for extensibility:
```julia
# Define abstract interface
abstract type AbstractOptimizationProblem end

# Existing implementation
struct LinearProblem <: AbstractOptimizationProblem
    A::Matrix
    b::Vector
end

# Solver works with any AbstractOptimizationProblem
function solve(problem::AbstractOptimizationProblem)
    # Generic solving logic
end

# NEW: Extend without modifying existing code
struct NonlinearProblem <: AbstractOptimizationProblem
    f::Function
    x0::Vector
end

# Solver automatically works with new type via multiple dispatch
```

❌ **Bad** - Hard-coded type checks:
```julia
function solve(problem)
    if problem isa LinearProblem
        # Linear solving logic
    elseif problem isa NonlinearProblem
        # Nonlinear solving logic
    # Need to modify this function for every new problem type!
    end
end
```

**How to Apply in Julia**:
- Use abstract types to define interfaces
- Leverage multiple dispatch for extensibility
- Avoid type checking with `isa` or `typeof`
- Design type hierarchies that allow new subtypes

**Red Flags**:
- Long chains of `if-elseif` checking types
- Functions that need modification for every new type
- Hard-coded lists of concrete types

---

### L - Liskov Substitution Principle (LSP)

**Definition**: Objects of a supertype should be replaceable with objects of a subtype without breaking the program. Subtypes must honor the contract of their parent type.

**Benefits**:
- Predictable behavior across type hierarchy
- Safe polymorphism
- Reusable generic code
- Fewer surprises

**Julia Examples**:

✅ **Good** - Consistent interface:
```julia
abstract type AbstractModel end

# Contract: all models must implement `evaluate`
function evaluate(model::AbstractModel, x)
    error("evaluate not implemented for $(typeof(model))")
end

# Subtype honors the contract
struct LinearModel <: AbstractModel
    coeffs::Vector
end

function evaluate(model::LinearModel, x)
    return dot(model.coeffs, x)  # Returns a number, as expected
end

# Another subtype also honors the contract
struct QuadraticModel <: AbstractModel
    A::Matrix
    b::Vector
end

function evaluate(model::QuadraticModel, x)
    return x' * model.A * x + dot(model.b, x)  # Returns a number
end

# Generic code works with any AbstractModel
function optimize(model::AbstractModel, x0)
    # Can safely call evaluate on any model
    value = evaluate(model, x0)
    # ...
end
```

❌ **Bad** - Subtype breaks parent contract:
```julia
abstract type AbstractModel end

struct LinearModel <: AbstractModel
    coeffs::Vector
end

function evaluate(model::LinearModel, x)
    return dot(model.coeffs, x)  # Returns a number
end

struct BrokenModel <: AbstractModel
    data::String
end

function evaluate(model::BrokenModel, x)
    return "error: invalid model"  # Returns a String! Breaks contract!
end

# This will fail unexpectedly
function optimize(model::AbstractModel, x0)
    value = evaluate(model, x0)
    gradient = value * 2  # ERROR if value is a String!
end
```

**How to Apply in Julia**:
- Define clear contracts for abstract types (via docstrings)
- Ensure all subtypes implement required methods consistently
- Return types should be compatible across the hierarchy
- Test that generic code works with all subtypes

**Red Flags**:
- Subtypes that throw errors for methods that should work
- Inconsistent return types across subtypes
- Subtypes that require special handling in generic code

---

### I - Interface Segregation Principle (ISP)

**Definition**: Clients should not be forced to depend on interfaces they don't use. Keep interfaces small and focused.

**Benefits**:
- Simpler, more focused interfaces
- Easier to implement
- Reduced coupling
- More flexible design

**Julia Examples**:

✅ **Good** - Small, focused interfaces using Holy Traits:
```julia
# Define trait types
abstract type EvaluableTrait end
struct IsEvaluable <: EvaluableTrait end
struct NotEvaluable <: EvaluableTrait end

abstract type DifferentiableTrait end
struct IsDifferentiable <: DifferentiableTrait end
struct NotDifferentiable <: DifferentiableTrait end

# Types implement only what they need
struct SimpleFunction
    f::Function
end

struct SmoothFunction
    f::Function
    df::Function
end

# Declare traits for each type
EvaluableTrait(::Type{<:SimpleFunction}) = IsEvaluable()
DifferentiableTrait(::Type{<:SimpleFunction}) = NotDifferentiable()

EvaluableTrait(::Type{<:SmoothFunction}) = IsEvaluable()
DifferentiableTrait(::Type{<:SmoothFunction}) = IsDifferentiable()

# Dispatch on traits
evaluate(f, x) = evaluate(EvaluableTrait(typeof(f)), f, x)
evaluate(::IsEvaluable, f, x) = f.f(x)

gradient(f, x) = gradient(DifferentiableTrait(typeof(f)), f, x)
gradient(::IsDifferentiable, f, x) = f.df(x)

# Clients depend only on what they need
function plot_function(f, xs)
    # Only needs evaluate capability
    return [evaluate(f, x) for x in xs]
end

function optimize(f, x0)
    # Only needs gradient capability
    return gradient_descent(f, x0)
end
```

❌ **Bad** - Bloated interface:
```julia
# Forces all types to implement everything
abstract type MathFunction end

# Required methods (even if not needed):
evaluate(f::MathFunction, x) = error("not implemented")
gradient(f::MathFunction, x) = error("not implemented")
hessian(f::MathFunction, x) = error("not implemented")
integrate(f::MathFunction, a, b) = error("not implemented")
fourier_transform(f::MathFunction) = error("not implemented")

# Simple function forced to implement everything
struct SimpleFunction <: MathFunction
    f::Function
end

evaluate(sf::SimpleFunction, x) = sf.f(x)
# Must implement all other methods even though they don't make sense!
gradient(sf::SimpleFunction, x) = error("not differentiable")
hessian(sf::SimpleFunction, x) = error("not differentiable")
# ... etc
```

**How to Apply in Julia**:
- Create small, focused abstract types
- Use `Union` types when something implements multiple interfaces
- Export only necessary functions
- Don't force implementations of unused methods

**Red Flags**:
- Abstract types with many required methods
- Types that throw "not implemented" for many methods
- Modules that export dozens of functions

---

### D - Dependency Inversion Principle (DIP)

**Definition**: High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details; details should depend on abstractions.

**Benefits**:
- Loose coupling
- Easier to test (can use mocks)
- Easier to swap implementations
- More flexible architecture

**Julia Examples**:

✅ **Good** - Depend on abstractions:
```julia
# High-level abstraction
abstract type DataStore end

# High-level module depends on abstraction
struct DataProcessor
    store::DataStore  # Depends on abstract type
end

function process(dp::DataProcessor, data)
    # Works with any DataStore implementation
    save(dp.store, data)
end

# Low-level implementations depend on abstraction
struct FileStore <: DataStore
    path::String
end

function save(fs::FileStore, data)
    write(fs.path, data)
end

struct DatabaseStore <: DataStore
    connection::DBConnection
end

function save(ds::DatabaseStore, data)
    execute(ds.connection, "INSERT ...", data)
end

# Easy to swap implementations
processor1 = DataProcessor(FileStore("data.txt"))
processor2 = DataProcessor(DatabaseStore(conn))
```

❌ **Bad** - Depend on concrete implementations:
```julia
# High-level module depends on low-level concrete type
struct DataProcessor
    file_path::String  # Tightly coupled to file system
end

function process(dp::DataProcessor, data)
    # Hard-coded to use files
    write(dp.file_path, data)
end

# Can't easily switch to database or other storage
# Would need to modify DataProcessor
```

**How to Apply in Julia**:
- Define abstract types for dependencies
- Pass abstract types as arguments
- Use dependency injection (pass dependencies to constructors)
- Avoid hard-coding concrete types

**Red Flags**:
- Structs with concrete type fields that could be abstract
- Hard-coded dependencies (e.g., file paths, URLs)
- Difficulty in testing due to external dependencies

---

## Other Design Principles

### DRY - Don't Repeat Yourself

**Definition**: Avoid code duplication. Every piece of knowledge should have a single, authoritative representation.

**Benefits**:
- Easier maintenance (change in one place)
- Reduced bugs (no inconsistent copies)
- Clearer code organization

**Julia Examples**:

✅ **Good** - Extract common logic:
```julia
# Common validation logic extracted
function validate_positive(x, name)
    x > 0 || throw(ArgumentError("$name must be positive"))
end

function create_model(n::Int, m::Int)
    validate_positive(n, "n")
    validate_positive(m, "m")
    return Model(n, m)
end
```

❌ **Bad** - Duplicated validation:
```julia
function create_model(n::Int, m::Int)
    n > 0 || throw(ArgumentError("n must be positive"))
    m > 0 || throw(ArgumentError("m must be positive"))
    return Model(n, m)
end

function create_problem(n::Int, m::Int)
    n > 0 || throw(ArgumentError("n must be positive"))  # Duplicated!
    m > 0 || throw(ArgumentError("m must be positive"))  # Duplicated!
    return Problem(n, m)
end
```

**How to Detect**:
```bash
# Look for similar code patterns
grep -r "similar_pattern" src/
# Use tools like `simian` or manual code review
```

---

### KISS - Keep It Simple, Stupid

**Definition**: Prefer simple solutions over complex ones. Avoid over-engineering.

**Benefits**:
- Easier to understand
- Easier to maintain
- Fewer bugs
- Faster development

**Julia Examples**:

✅ **Good** - Simple and clear:
```julia
function compute_mean(xs)
    return sum(xs) / length(xs)
end
```

❌ **Bad** - Over-engineered:
```julia
# Unnecessary abstraction and complexity
abstract type Aggregator end
struct MeanAggregator <: Aggregator
    strategy::Symbol
end

function aggregate(agg::MeanAggregator, xs)
    if agg.strategy == :simple
        return sum(xs) / length(xs)
    elseif agg.strategy == :weighted
        # Not even used!
        error("not implemented")
    end
end

# Usage is unnecessarily complex
compute_mean(xs) = aggregate(MeanAggregator(:simple), xs)
```

**Red Flags**:
- Abstractions that are only used once
- Complex inheritance hierarchies for simple problems
- "Future-proofing" that's never needed

---

### YAGNI - You Aren't Gonna Need It

**Definition**: Don't implement functionality until it's actually needed.

**Benefits**:
- Less code to maintain
- Faster development
- Avoid wasted effort on unused features

**Julia Examples**:

✅ **Good** - Implement only what's needed:
```julia
# Simple struct with only required fields
struct Model
    n::Int
    m::Int
end
```

❌ **Bad** - Speculative features:
```julia
# Adding fields "just in case"
struct Model
    n::Int
    m::Int
    name::String  # Not used anywhere
    metadata::Dict  # Not used anywhere
    version::Int  # Not used anywhere
    created_at::DateTime  # Not used anywhere
end
```

---

### POLA - Principle of Least Astonishment

**Definition**: Software should behave in a way that least surprises users. Names and behaviors should be intuitive.

**Benefits**:
- Easier to learn and use
- Fewer mistakes
- Better user experience

**Julia Examples**:

✅ **Good** - Clear, unsurprising names:
```julia
function compute_gradient(f, x)
    # Does what the name says
    return ForwardDiff.gradient(f, x)
end

function solve_linear_system(A, b)
    # Clear what it does
    return A \ b
end
```

❌ **Bad** - Surprising behavior:
```julia
function process(x)
    # Name doesn't indicate it modifies x!
    x .= x .* 2
    return x
end

function get_data()
    # Name suggests reading, but it also writes!
    data = read_file("input.txt")
    write_file("log.txt", "Data accessed")
    return data
end
```

**Guidelines**:
- Use clear, descriptive names
- Avoid side effects in functions with "get" or "compute"
- Follow Julia conventions (e.g., `!` for mutating functions)
- Document unexpected behavior

---

### POLP - Principle of Least Privilege

**Definition**: Expose only what's necessary. Keep implementation details private.

**Benefits**:
- Simpler public API
- Easier to change internals
- Reduced coupling
- Better security

**Julia Examples**:

✅ **Good** - Minimal exports:
```julia
module MyPackage

# Only export what users need
export solve, Model

# Public API
struct Model
    # Public fields
end

function solve(model::Model)
    # Uses internal functions
    validated = _validate(model)
    result = _compute(validated)
    return _format(result)
end

# Internal functions (not exported)
_validate(model) = ...
_compute(data) = ...
_format(result) = ...

end  # module
```

❌ **Bad** - Everything exported:
```julia
module MyPackage

# Exporting everything!
export solve, Model, _validate, _compute, _format, 
       _helper1, _helper2, _internal_state, ...

# Users can access internals, making it hard to change later
```

**Guidelines**:
- Export only public API functions
- Use `_` prefix for internal functions
- Document what's public vs internal
- Keep struct fields minimal

---

## Quality Objectives

These are the four key quality dimensions to consider when designing software.

### 1. Reusability

**Definition**: The degree to which components can be reused in different contexts.

**Characteristics**:
- Modular, independent components
- Clear, well-defined interfaces
- Minimal coupling
- Generic, composable design

**How to Assess**:
- Can this function/type be used in other contexts?
- Are dependencies minimal?
- Is the interface clear and documented?
- Does it follow SOLID principles?

**Julia-Specific**:
- Use parametric types for genericity
- Leverage multiple dispatch
- Create small, composable functions
- Use abstract types for interfaces

**Score Guide**:
- **5/5**: Highly generic, used in multiple contexts
- **4/5**: Modular, could be reused with minor changes
- **3/5**: Somewhat specific but has reusable parts
- **2/5**: Tightly coupled, hard to extract
- **1/5**: Completely context-specific

---

### 2. Performance

**Definition**: The efficiency of code in terms of speed and memory usage.

**Characteristics** (Julia-specific):
- Type-stable code
- Minimal allocations
- Efficient algorithms
- Proper use of Julia features

**How to Assess**:
```julia
# Type stability
@code_warntype function_name(args...)

# Allocations
@time function_name(args...)
@allocated function_name(args...)

# Profiling
using Profile
@profile function_name(args...)
```

**Key Considerations**:
- Avoid type instabilities (red in `@code_warntype`)
- Minimize allocations in hot loops
- Use `@inbounds` safely for performance
- Avoid global variables in performance-critical code
- Use views instead of copies when possible

**Score Guide**:
- **5/5**: Type-stable, minimal allocations, optimized
- **4/5**: Mostly efficient, minor improvements possible
- **3/5**: Acceptable performance, some inefficiencies
- **2/5**: Performance issues, needs optimization
- **1/5**: Severe performance problems

---

### 3. Maintainability

**Definition**: The ease with which code can be understood, modified, and extended.

**Characteristics**:
- Clear, readable code
- Good documentation
- Reasonable complexity
- Follows conventions
- No technical debt

**How to Assess**:
- Is the code self-documenting?
- Are functions reasonably sized (<50 lines)?
- Is there duplicate code?
- Are there TODOs or FIXMEs?
- Does it follow project conventions?

**Key Considerations**:
- Use descriptive names
- Add docstrings to public functions
- Keep functions focused (SRP)
- Avoid deep nesting
- Use consistent style

**Score Guide**:
- **5/5**: Crystal clear, well-documented, easy to modify
- **4/5**: Clear, minor documentation gaps
- **3/5**: Understandable with effort
- **2/5**: Confusing, poor documentation
- **1/5**: Unmaintainable, needs refactoring

---

### 4. Safety

**Definition**: The degree to which code handles errors, validates inputs, and avoids bugs.

**Characteristics**:
- Input validation
- Error handling
- Edge case handling
- Type safety
- Minimal mutable state

**How to Assess**:
- Are inputs validated?
- Are errors handled gracefully?
- Are edge cases tested?
- Is `missing` data handled?
- Are types used to prevent errors?

**Julia-Specific**:
- Use `Union{T, Nothing}` for optional values
- Handle `missing` data appropriately
- Use type annotations to catch errors early
- Validate preconditions
- Use `@assert` for invariants

**Score Guide**:
- **5/5**: Robust error handling, all edge cases covered
- **4/5**: Good error handling, minor gaps
- **3/5**: Basic error handling, some edge cases missed
- **2/5**: Poor error handling, many edge cases missed
- **1/5**: No error handling, unsafe

---

## Julia-Specific Considerations

### Type Stability

**Critical for performance**. A function is type-stable if the type of the output can be inferred from the types of the inputs.

```julia
# Check type stability
@code_warntype function_name(args...)
```

**Red flags**:
- `Any` in inferred types
- Red warnings in `@code_warntype`
- Unions that are too broad

### Multiple Dispatch

**Use it for extensibility** (Open/Closed Principle):

```julia
# Define generic interface
function solve(problem::AbstractProblem)
    error("solve not implemented for $(typeof(problem))")
end

# Extend for specific types
solve(p::LinearProblem) = ...
solve(p::NonlinearProblem) = ...
```

### Type Piracy

**Avoid it** (violates Open/Closed and can cause conflicts):

```julia
# ❌ BAD: Extending external function on external type
Base.+(x::SomeExternalType, y::SomeExternalType) = ...

# ✅ GOOD: Define your own function or type
myoperation(x::SomeExternalType, y::SomeExternalType) = ...
```

### Parametric Types

**Use for reusability**:

```julia
# Generic container
struct Container{T}
    data::Vector{T}
end

# Works with any type
Container([1, 2, 3])        # Container{Int64}
Container([1.0, 2.0, 3.0])  # Container{Float64}
```

### Abstract Types in Struct Fields

**Avoid for performance**:

```julia
# ❌ BAD: Abstract type field (type instability)
struct Model
    optimizer::AbstractOptimizer
end

# ✅ GOOD: Parametric type
struct Model{O <: AbstractOptimizer}
    optimizer::O
end
```

---

## Quick Reference Checklists

### Planning Checklist

When planning a new feature:

**SOLID**:
- [ ] Each component has a single responsibility (S)
- [ ] Design allows extension without modification (O)
- [ ] Type hierarchies are consistent (L)
- [ ] Interfaces are minimal and focused (I)
- [ ] Dependencies are via abstractions (D)

**Other Principles**:
- [ ] No duplication of existing functionality (DRY)
- [ ] Simplest solution that works (KISS)
- [ ] Only implementing what's needed (YAGNI)
- [ ] API is intuitive and unsurprising (POLA)
- [ ] Minimal exports planned (POLP)

**Quality Objectives**:
- [ ] Reusability: Components are modular and composable
- [ ] Performance: Type stability and efficiency considered
- [ ] Maintainability: Clear design, good documentation planned
- [ ] Safety: Error handling and validation planned

---

### Code Review Checklist

When reviewing code:

**SOLID**:
- [ ] Functions/modules have single responsibility
- [ ] Code can be extended without modification
- [ ] Subtypes honor parent contracts
- [ ] Interfaces are not bloated
- [ ] Dependencies are via abstractions

**Other Principles**:
- [ ] No code duplication
- [ ] No unnecessary complexity
- [ ] No speculative features
- [ ] Behavior is unsurprising
- [ ] Minimal API surface

**Quality**:
- [ ] Code is reusable and modular
- [ ] Performance is acceptable (check `@code_warntype`)
- [ ] Code is maintainable and clear
- [ ] Error handling is robust

**Julia-Specific**:
- [ ] Type-stable code
- [ ] No type piracy
- [ ] Appropriate use of abstract types
- [ ] Proper exports

---

### Testing Checklist

When writing tests:

**Functional Tests**:
- [ ] All public functions tested
- [ ] Edge cases covered
- [ ] Error conditions tested

**Quality Tests**:
- [ ] Performance tests (if critical): `@test (@allocated ...) < threshold`
- [ ] Type stability tests: `@test_nowarn @inferred function_name(...)`
- [ ] Interface contract tests (LSP)
- [ ] Error handling tests: `@test_throws`

---

## References

### Books
- **"Hands-On Design Patterns and Best Practices with Julia"** by Tom Kwong
  - Comprehensive guide to design patterns in Julia
  - Adapts SOLID principles to Julia's paradigm
  - Excellent examples and anti-patterns

### Online Resources
- [Julia Performance Tips](https://docs.julialang.org/en/v1/manual/performance-tips/)
- [Julia Style Guide](https://docs.julialang.org/en/v1/manual/style-guide/)
- [SOLID Principles (Wikipedia)](https://en.wikipedia.org/wiki/SOLID)

### Tools
- `JuliaFormatter.jl` - Code formatting
- `Aqua.jl` - Package quality checks
- `JET.jl` - Static type analysis
- `@code_warntype` - Type stability analysis
- `@time`, `@allocated` - Performance profiling

---

## Version History

- **v1.0** (2025-12-31): Initial version with SOLID, DRY, KISS, YAGNI, POLA, POLP, and Quality Objectives

---

**Note**: This is a living document. As the team learns and evolves, this reference should be updated to reflect new insights and best practices.
