#ifndef DKUK_ASYNCRONIZER_HPP
#define DKUK_ASYNCRONIZER_HPP

#include <memory>

#include <pybind11/pybind11.h>


namespace dkuk {
namespace asyncronizer {


template<class T, class... Ts>
using shared_ptr_managed_class = pybind11::class_<T, std::shared_ptr<T>, Ts...>;


};	// namespace asyncronizer
};	// namespace dkuk

#endif	// DKUK_ASYNCRONIZER_HPP
