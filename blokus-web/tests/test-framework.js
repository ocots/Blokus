/**
 * Simple test framework for browser-based tests
 * @module test-framework
 */

let testResults = { passed: 0, failed: 0, errors: [] };

/**
 * Reset test results
 */
export function resetTests() {
    testResults = { passed: 0, failed: 0, errors: [] };
}

/**
 * Assert that a condition is true
 * @param {boolean} condition
 * @param {string} message
 */
export function assert(condition, message) {
    if (condition) {
        testResults.passed++;
    } else {
        testResults.failed++;
        testResults.errors.push(`❌ FAIL: ${message}`);
        console.error(`❌ FAIL: ${message}`);
    }
}

/**
 * Assert equality
 * @param {*} actual
 * @param {*} expected
 * @param {string} message
 */
export function assertEqual(actual, expected, message) {
    const pass = JSON.stringify(actual) === JSON.stringify(expected);
    if (pass) {
        testResults.passed++;
    } else {
        testResults.failed++;
        const error = `❌ FAIL: ${message}\n   Expected: ${JSON.stringify(expected)}\n   Actual: ${JSON.stringify(actual)}`;
        testResults.errors.push(error);
        console.error(error);
    }
}

/**
 * Assert that values are not equal
 * @param {*} actual
 * @param {*} notExpected
 * @param {string} message
 */
export function assertNotEqual(actual, notExpected, message) {
    const pass = JSON.stringify(actual) !== JSON.stringify(notExpected);
    if (pass) {
        testResults.passed++;
    } else {
        testResults.failed++;
        const error = `❌ FAIL: ${message}\n   Should not equal: ${JSON.stringify(notExpected)}`;
        testResults.errors.push(error);
        console.error(error);
    }
}

/**
 * Run a test suite
 * @param {string} name
 * @param {Function} fn
 */
export function describe(name, fn) {
    console.log(`\n📁 ${name}`);
    fn();
}

/**
 * Run a single test
 * @param {string} name
 * @param {Function} fn
 */
export function test(name, fn) {
    try {
        fn();
        console.log(`  ✅ ${name}`);
    } catch (e) {
        testResults.failed++;
        testResults.errors.push(`❌ ERROR in "${name}": ${e.message}`);
        console.error(`  ❌ ${name}: ${e.message}`);
    }
}

/**
 * Print test summary
 */
export function printSummary() {
    console.log('\n' + '='.repeat(50));
    console.log(`📊 Test Results: ${testResults.passed} passed, ${testResults.failed} failed`);
    
    if (testResults.errors.length > 0) {
        console.log('\nErrors:');
        testResults.errors.forEach(e => console.log(e));
    }
    
    console.log('='.repeat(50));
    
    return testResults;
}

/**
 * Get test results
 * @returns {{passed: number, failed: number, errors: string[]}}
 */
export function getResults() {
    return { ...testResults };
}
