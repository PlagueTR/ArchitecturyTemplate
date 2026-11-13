package com.example.example_mod.fabric;

import com.example.example_mod.Main;

import net.fabricmc.api.ModInitializer;

public final class MainFabric implements ModInitializer {

    @Override
    public void onInitialize() {
        Main.init();
    }

}
