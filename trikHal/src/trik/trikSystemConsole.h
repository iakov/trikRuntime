/* Copyright 2015 Yurii Litvinov and CyberTech Labs Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License. */

#pragma once

#include "systemConsoleInterface.h"

namespace trikHal {
namespace trik {

/// Real implementation of system console.
class TrikSystemConsole : public SystemConsoleInterface
{
public:
	int system(const QString &command) override;
	bool startProcess(const QString &processName, const QStringList &arguments) override;
	bool startProcessSynchronously(const QString &processName, const QStringList &arguments
			, QString * output = nullptr) override;
};

}
}
