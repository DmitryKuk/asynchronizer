#ifndef DKUK_ASYNCHRONIZER_HPP
#define DKUK_ASYNCHRONIZER_HPP

#include <memory>

#include <pybind11/pybind11.h>


namespace dkuk {
namespace asynchronizer {


template<class T, class... Ts>
using shared_ptr_managed_class = pybind11::class_<T, std::shared_ptr<T>, Ts...>;


};	// namespace asynchronizer
};	// namespace dkuk

#endif	// DKUK_ASYNCHRONIZER_HPP
