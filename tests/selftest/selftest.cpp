/* Copyright 2015 CyberTech Labs Ltd.
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

#include <QtCore/QScopedPointer>

#include <trikControl/brickInterface.h>
#include <trikControl/brickFactory.h>
#include <trikKernel/configurer.h>
#include <trikNetwork/gamepadFactory.h>
#include <trikNetwork/gamepadInterface.h>
#include <trikNetwork/mailboxFactory.h>
#include <trikNetwork/mailboxInterface.h>

#include <gtest/gtest.h>
#include <gmock/gmock.h>

using namespace testing;
using namespace trikControl;
using namespace trikNetwork;

TEST(selftest, brickCheck)
{
	QScopedPointer<BrickInterface> brick(BrickFactory::create(*QThread::currentThread(), "./", "./"));

	EXPECT_TRUE(brick->battery() != nullptr);
	if (brick->battery() != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->battery()->status());
		EXPECT_THAT(0.0, Not(DoubleEq(brick->battery()->readVoltage())));
	}


	EXPECT_TRUE(brick->encoder("B1") != nullptr);
	if (brick->encoder("B1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->encoder("B1")->status());
	}

	EXPECT_TRUE(brick->encoder("B2") != nullptr);
	if (brick->encoder("B2") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->encoder("B2")->status());
	}

	EXPECT_TRUE(brick->encoder("B3") != nullptr);
	if (brick->encoder("B3") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->encoder("B3")->status());
	}

	EXPECT_TRUE(brick->encoder("B4") != nullptr);
	if (brick->encoder("B4") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->encoder("B4")->status());
	}


	EXPECT_TRUE(brick->keys() != nullptr);
	if (brick->keys() != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->keys()->status());
	}

	EXPECT_TRUE(brick->led() != nullptr);
	if (brick->led() != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->led()->status());
	}


	EXPECT_TRUE(brick->motor("M1") != nullptr);
	if (brick->motor("M1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("M1")->status());
	}

	EXPECT_TRUE(brick->motor("M2") != nullptr);
	if (brick->motor("M1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("M2")->status());
	}

	EXPECT_TRUE(brick->motor("M3") != nullptr);
	if (brick->motor("M1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("M3")->status());
	}

	EXPECT_TRUE(brick->motor("M4") != nullptr);
	if (brick->motor("M1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("M4")->status());
	}


	EXPECT_TRUE(brick->motor("E1") != nullptr);
	if (brick->motor("E1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("E1")->status());
	}

	EXPECT_TRUE(brick->motor("E2") != nullptr);
	if (brick->motor("E2") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("E2")->status());
	}

	EXPECT_TRUE(brick->motor("E3") != nullptr);
	if (brick->motor("E3") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("E3")->status());
	}

	EXPECT_TRUE(brick->motor("C1") != nullptr);
	if (brick->motor("C1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("C1")->status());
	}

	EXPECT_TRUE(brick->motor("C2") != nullptr);
	if (brick->motor("C2") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("C2")->status());
	}

	EXPECT_TRUE(brick->motor("C3") != nullptr);
	if (brick->motor("C3") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->motor("C3")->status());
	}


	EXPECT_TRUE(brick->sensor("A1") != nullptr);
	if (brick->sensor("A1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("A1")->status());
	}

	EXPECT_TRUE(brick->sensor("A2") != nullptr);
	if (brick->sensor("A2") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("A2")->status());
	}

	EXPECT_TRUE(brick->sensor("A3") != nullptr);
	if (brick->sensor("A3") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("A3")->status());
	}

	EXPECT_TRUE(brick->sensor("A4") != nullptr);
	if (brick->sensor("A4") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("A4")->status());
	}

	EXPECT_TRUE(brick->sensor("A5") != nullptr);
	if (brick->sensor("A5") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("A5")->status());
	}

	EXPECT_TRUE(brick->sensor("A6") != nullptr);
	if (brick->sensor("A6") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("A6")->status());
	}


	EXPECT_TRUE(brick->sensor("D1") != nullptr);
	if (brick->sensor("D1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("D1")->status());
	}

	EXPECT_TRUE(brick->sensor("D2") != nullptr);
	if (brick->sensor("D2") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("D2")->status());
	}


	EXPECT_TRUE(brick->sensor("F1") != nullptr);
	if (brick->sensor("F1") != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->sensor("F1")->status());
	}


	EXPECT_TRUE(brick->accelerometer() != nullptr);
	if (brick->accelerometer() != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->accelerometer()->status());
	}

	EXPECT_TRUE(brick->gyroscope() != nullptr);
	if (brick->gyroscope() != nullptr) {
		EXPECT_EQ(DeviceInterface::Status::ready, brick->gyroscope()->status());
	}
}

TEST(selftest, mailboxCheck)
{
	trikKernel::Configurer configurer(".");
	QScopedPointer<MailboxInterface> mailbox(MailboxFactory::create(configurer));
	ASSERT_FALSE(mailbox.isNull());
}

TEST(selftest, gamepadCheck)
{
//	trikKernel::Configurer configurer(".");
//	QScopedPointer<GamepadInterface> gamepad(GamepadFactory::create(configurer));
//	ASSERT_FALSE(gamepad.isNull());
}
